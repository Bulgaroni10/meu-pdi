import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import OwnedModel
from .validators import validar_imagem_evidencia


def caminho_imagem_evidencia(instance, filename):
    extensao = Path(filename).suffix.lower()
    return (
        f"usuarios/{instance.usuario_id}/projetos/evidencias/"
        f"{uuid.uuid4().hex}{extensao}"
    )


class Projeto(OwnedModel):
    class Status(models.TextChoices):
        IDEIA = "ideia", "Ideia"
        PLANEJADO = "planejado", "Planejado"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        PAUSADO = "pausado", "Pausado"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"

    titulo = models.CharField("título", max_length=180)
    objetivo = models.ForeignKey(
        "objetivos.Objetivo",
        on_delete=models.PROTECT,
        related_name="projetos",
        blank=True,
        null=True,
    )
    problema = models.TextField("problema ou oportunidade", blank=True)
    solucao = models.TextField("solução proposta", blank=True)
    data_inicio = models.DateField("data de início", default=timezone.localdate)
    prazo = models.DateField("prazo", blank=True, null=True)
    data_conclusao = models.DateField("data de conclusão", blank=True, null=True)
    status = models.CharField(
        "status", max_length=20, choices=Status.choices, default=Status.IDEIA
    )
    progresso = models.PositiveSmallIntegerField("progresso", default=0)
    resultado = models.TextField("resultado alcançado", blank=True)
    aprendizados = models.TextField("aprendizados", blank=True)
    repositorio_url = models.URLField("repositório", blank=True)
    demonstracao_url = models.URLField("demonstração", blank=True)
    arquivado_em = models.DateTimeField("arquivado em", blank=True, null=True)

    class Meta:
        ordering = ("-updated_at",)
        indexes = [
            models.Index(fields=("usuario", "status"), name="projeto_usuario_status_idx"),
            models.Index(fields=("usuario", "prazo"), name="projeto_usuario_prazo_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(progresso__gte=0, progresso__lte=100),
                name="projeto_progresso_0_100",
            )
        ]

    def __str__(self):
        return self.titulo

    def clean(self):
        if self.objetivo_id and self.objetivo.usuario_id != self.usuario_id:
            raise ValidationError({"objetivo": "Selecione um objetivo do seu perfil."})
        if self.prazo and self.prazo < self.data_inicio:
            raise ValidationError({"prazo": "O prazo não pode ser anterior ao início."})

    def save(self, *args, **kwargs):
        if self.status == self.Status.CONCLUIDO:
            self.progresso = 100
            self.data_conclusao = self.data_conclusao or timezone.localdate()
        elif self.data_conclusao:
            self.data_conclusao = None
        super().save(*args, **kwargs)


class Tecnologia(OwnedModel):
    class Categoria(models.TextChoices):
        LINGUAGEM = "linguagem", "Linguagem"
        FRAMEWORK = "framework", "Framework"
        NUVEM = "nuvem", "Nuvem"
        BANCO = "banco", "Banco de dados"
        INFRA = "infra", "Infraestrutura"
        FERRAMENTA = "ferramenta", "Ferramenta"
        OUTRO = "outro", "Outro"

    nome = models.CharField("nome", max_length=80)
    categoria = models.CharField(
        "categoria", max_length=20, choices=Categoria.choices, default=Categoria.FERRAMENTA
    )

    class Meta:
        ordering = ("nome",)
        constraints = [
            models.UniqueConstraint(
                fields=("usuario", "nome"), name="tecnologia_usuario_nome_unico"
            )
        ]

    def __str__(self):
        return self.nome


class ProjetoTecnologia(OwnedModel):
    projeto = models.ForeignKey(
        Projeto, on_delete=models.CASCADE, related_name="tecnologias_vinculadas"
    )
    tecnologia = models.ForeignKey(
        Tecnologia, on_delete=models.PROTECT, related_name="projetos_vinculados"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("projeto", "tecnologia"), name="projeto_tecnologia_unica"
            )
        ]

    def clean(self):
        if self.projeto_id and self.projeto.usuario_id != self.usuario_id:
            raise ValidationError("O projeto deve pertencer ao perfil pessoal.")
        if self.tecnologia_id and self.tecnologia.usuario_id != self.usuario_id:
            raise ValidationError("A tecnologia deve pertencer ao perfil pessoal.")


class MarcoProjeto(OwnedModel):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        CONCLUIDO = "concluido", "Concluído"

    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name="marcos")
    titulo = models.CharField("título", max_length=180)
    descricao = models.TextField("descrição", blank=True)
    prazo = models.DateField("prazo", blank=True, null=True)
    status = models.CharField(
        "status", max_length=20, choices=Status.choices, default=Status.PENDENTE
    )
    ordem = models.PositiveSmallIntegerField("ordem", default=1)

    class Meta:
        ordering = ("ordem", "prazo")
        constraints = [
            models.UniqueConstraint(
                fields=("projeto", "ordem"), name="marco_projeto_ordem_unica"
            )
        ]

    def __str__(self):
        return self.titulo


class TarefaProjeto(OwnedModel):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        CONCLUIDA = "concluida", "Concluída"

    class Prioridade(models.TextChoices):
        BAIXA = "baixa", "Baixa"
        MEDIA = "media", "Média"
        ALTA = "alta", "Alta"

    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name="tarefas")
    titulo = models.CharField("título", max_length=180)
    descricao = models.TextField("descrição", blank=True)
    prazo = models.DateField("prazo", blank=True, null=True)
    status = models.CharField(
        "status", max_length=20, choices=Status.choices, default=Status.PENDENTE
    )
    prioridade = models.CharField(
        "prioridade", max_length=10, choices=Prioridade.choices, default=Prioridade.MEDIA
    )
    ordem = models.PositiveSmallIntegerField("ordem", default=1)

    class Meta:
        ordering = ("ordem", "created_at")
        constraints = [
            models.UniqueConstraint(
                fields=("projeto", "ordem"), name="tarefa_projeto_ordem_unica"
            )
        ]

    def __str__(self):
        return self.titulo


class Evidencia(OwnedModel):
    class Tipo(models.TextChoices):
        LINK = "link", "Link"
        REPOSITORIO = "repositorio", "Repositório"
        DOCUMENTO = "documento", "Documento"
        CAPTURA = "captura", "Captura de tela"
        RESULTADO = "resultado", "Resultado"
        OUTRO = "outro", "Outro"

    projeto = models.ForeignKey(Projeto, on_delete=models.PROTECT, related_name="evidencias")
    tipo = models.CharField("tipo", max_length=20, choices=Tipo.choices)
    titulo = models.CharField("título", max_length=180)
    descricao = models.TextField("descrição")
    url = models.URLField("link", blank=True)
    material = models.ForeignKey(
        "biblioteca.MaterialPDF",
        on_delete=models.SET_NULL,
        related_name="evidencias_projeto",
        blank=True,
        null=True,
    )
    imagem = models.FileField(
        "imagem da captura",
        upload_to=caminho_imagem_evidencia,
        validators=[validar_imagem_evidencia],
        blank=True,
        help_text="PNG, JPG ou WebP, com no máximo 8 MB.",
    )
    data = models.DateField("data", default=timezone.localdate)
    validada = models.BooleanField("evidência validada", default=False)

    class Meta:
        ordering = ("-data", "-created_at")

    def __str__(self):
        return self.titulo

    def clean(self):
        if self.projeto_id and self.projeto.usuario_id != self.usuario_id:
            raise ValidationError({"projeto": "Selecione um projeto do seu perfil."})
        if self.material_id and self.material.usuario_id != self.usuario_id:
            raise ValidationError({"material": "Selecione um material do seu perfil."})
        if self.imagem and self.tipo != self.Tipo.CAPTURA:
            raise ValidationError(
                {"imagem": "Selecione o tipo Captura de tela para anexar uma imagem."}
            )
