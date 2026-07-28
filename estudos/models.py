from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import OwnedModel


class StatusEstudo(models.TextChoices):
    NAO_INICIADO = "nao_iniciado", "Não iniciado"
    PLANEJADO = "planejado", "Planejado"
    EM_ANDAMENTO = "em_andamento", "Em andamento"
    PAUSADO = "pausado", "Pausado"
    CONCLUIDO = "concluido", "Concluído"
    CANCELADO = "cancelado", "Cancelado"


class Trilha(OwnedModel):
    class Categoria(models.TextChoices):
        FACULDADE = "faculdade", "Faculdade"
        POS = "pos", "Pós-graduação"
        AZURE = "azure", "Azure"
        WINDOWS = "windows", "Windows Server"
        REDES = "redes", "Redes"
        SEGURANCA = "seguranca", "Segurança"
        POWERSHELL = "powershell", "PowerShell"
        PYTHON = "python", "Python"
        DEVOPS = "devops", "DevOps"
        OUTRO = "outro", "Outro"

    class Nivel(models.TextChoices):
        INICIANTE = "iniciante", "Iniciante"
        INTERMEDIARIO = "intermediario", "Intermediário"
        AVANCADO = "avancado", "Avançado"

    titulo = models.CharField("título", max_length=180)
    descricao = models.TextField("descrição", blank=True)
    categoria = models.CharField("categoria", max_length=20, choices=Categoria.choices)
    nivel = models.CharField(
        "nível", max_length=20, choices=Nivel.choices, default=Nivel.INICIANTE
    )
    prioridade = models.CharField(
        "prioridade",
        max_length=10,
        choices=[("baixa", "Baixa"), ("media", "Média"), ("alta", "Alta")],
        default="media",
    )
    data_inicio = models.DateField("data de início", default=timezone.localdate)
    prazo = models.DateField("prazo", blank=True, null=True)
    status = models.CharField(
        "status", max_length=20, choices=StatusEstudo.choices, default=StatusEstudo.PLANEJADO
    )
    progresso = models.PositiveSmallIntegerField("progresso", default=0)
    carga_horaria_prevista = models.DecimalField(
        "carga horária prevista", max_digits=7, decimal_places=1, default=0
    )
    carga_horaria_realizada = models.DecimalField(
        "carga horária realizada", max_digits=7, decimal_places=1, default=0
    )
    prerequisitos = models.TextField("pré-requisitos", blank=True)
    objetivo = models.ForeignKey(
        "objetivos.Objetivo",
        on_delete=models.PROTECT,
        related_name="trilhas",
        blank=True,
        null=True,
    )
    observacoes = models.TextField("observações", blank=True)

    class Meta:
        ordering = ("-updated_at",)
        indexes = [models.Index(fields=("usuario", "status"), name="trilha_usuario_status_idx")]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(progresso__gte=0, progresso__lte=100),
                name="trilha_progresso_0_100",
            )
        ]

    def __str__(self):
        return self.titulo

    def clean(self):
        if self.objetivo_id and self.objetivo.usuario_id != self.usuario_id:
            raise ValidationError({"objetivo": "Selecione um objetivo do seu perfil."})
        if self.prazo and self.prazo < self.data_inicio:
            raise ValidationError({"prazo": "O prazo não pode ser anterior ao início."})


class Curso(OwnedModel):
    class Tipo(models.TextChoices):
        GRADUACAO = "graduacao", "Graduação"
        POS = "pos", "Pós-graduação"
        LIVRE = "livre", "Curso livre"
        CERTIFICACAO = "certificacao", "Certificação"
        CORPORATIVO = "corporativo", "Treinamento"
        OUTRO = "outro", "Outro"

    nome = models.CharField("nome", max_length=180)
    instituicao = models.CharField("instituição", max_length=180, blank=True)
    tipo = models.CharField("tipo", max_length=20, choices=Tipo.choices)
    descricao = models.TextField("descrição", blank=True)
    data_inicio = models.DateField("data de início", blank=True, null=True)
    data_prevista_conclusao = models.DateField("conclusão prevista", blank=True, null=True)
    data_real_conclusao = models.DateField("conclusão real", blank=True, null=True)
    status = models.CharField(
        "status", max_length=20, choices=StatusEstudo.choices, default=StatusEstudo.PLANEJADO
    )
    carga_horaria = models.DecimalField(
        "carga horária", max_digits=7, decimal_places=1, default=0
    )
    trilhas = models.ManyToManyField(Trilha, related_name="cursos", blank=True)
    observacoes = models.TextField("observações", blank=True)

    class Meta:
        ordering = ("-updated_at",)
        indexes = [models.Index(fields=("usuario", "status"), name="curso_usuario_status_idx")]

    def __str__(self):
        return self.nome


class Periodo(OwnedModel):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="periodos")
    nome = models.CharField("nome", max_length=100)
    numero = models.PositiveSmallIntegerField("número", default=1)
    data_inicio = models.DateField("data de início", blank=True, null=True)
    data_conclusao = models.DateField("data de conclusão", blank=True, null=True)
    status = models.CharField(
        "status", max_length=20, choices=StatusEstudo.choices, default=StatusEstudo.PLANEJADO
    )
    observacoes = models.TextField("observações", blank=True)

    class Meta:
        ordering = ("numero",)
        constraints = [
            models.UniqueConstraint(fields=("curso", "numero"), name="periodo_curso_numero_unico")
        ]

    def __str__(self):
        return f"{self.curso} - {self.nome}"

    def clean(self):
        if self.curso_id and self.curso.usuario_id != self.usuario_id:
            raise ValidationError({"curso": "Selecione um curso do seu perfil."})


class Disciplina(OwnedModel):
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name="disciplinas")
    periodo = models.ForeignKey(
        Periodo, on_delete=models.PROTECT, related_name="disciplinas", blank=True, null=True
    )
    nome = models.CharField("nome", max_length=180)
    codigo = models.CharField("código", max_length=40, blank=True)
    professor = models.CharField("professor", max_length=180, blank=True)
    descricao = models.TextField("descrição", blank=True)
    carga_horaria = models.DecimalField(
        "carga horária", max_digits=7, decimal_places=1, default=0
    )
    status = models.CharField(
        "status", max_length=20, choices=StatusEstudo.choices, default=StatusEstudo.PLANEJADO
    )
    nota = models.DecimalField("nota", max_digits=5, decimal_places=2, blank=True, null=True)
    frequencia = models.DecimalField(
        "frequência (%)", max_digits=5, decimal_places=2, blank=True, null=True
    )
    progresso = models.PositiveSmallIntegerField("progresso", default=0)
    ementa = models.TextField("ementa", blank=True)
    observacoes = models.TextField("observações", blank=True)

    class Meta:
        ordering = ("nome",)
        indexes = [models.Index(fields=("usuario", "status"), name="disciplina_usuario_status_idx")]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(progresso__gte=0, progresso__lte=100),
                name="disciplina_progresso_0_100",
            )
        ]

    def __str__(self):
        return self.nome

    def clean(self):
        if self.curso_id and self.curso.usuario_id != self.usuario_id:
            raise ValidationError({"curso": "Selecione um curso do seu perfil."})
        if self.periodo_id and self.periodo.curso_id != self.curso_id:
            raise ValidationError({"periodo": "O período deve pertencer ao curso selecionado."})


class Aula(OwnedModel):
    class Dificuldade(models.TextChoices):
        FACIL = "facil", "Fácil"
        MEDIA = "media", "Média"
        DIFICIL = "dificil", "Difícil"

    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT, related_name="aulas")
    titulo = models.CharField("título", max_length=180)
    numero = models.PositiveSmallIntegerField("número da aula", default=1)
    data = models.DateField("data", default=timezone.localdate)
    professor = models.CharField("professor", max_length=180, blank=True)
    descricao = models.TextField("descrição", blank=True)
    status = models.CharField(
        "status", max_length=20, choices=StatusEstudo.choices, default=StatusEstudo.PLANEJADO
    )
    duracao_prevista = models.PositiveIntegerField("duração prevista (min)", default=0)
    duracao_estudada = models.PositiveIntegerField("duração estudada (min)", default=0)
    dificuldade = models.CharField(
        "dificuldade", max_length=10, choices=Dificuldade.choices, default=Dificuldade.MEDIA
    )
    resumo = models.TextField("resumo", blank=True)
    duvidas = models.TextField("dúvidas", blank=True)
    aplicacao_pratica = models.TextField("aplicação prática", blank=True)
    proxima_revisao = models.DateField("próxima revisão", blank=True, null=True)
    concluida = models.BooleanField("concluída", default=False)
    favorita = models.BooleanField("favorita", default=False)
    tags = models.CharField("tags", max_length=240, blank=True)

    class Meta:
        ordering = ("-data", "-numero")
        indexes = [
            models.Index(fields=("usuario", "disciplina", "data"), name="aula_usuario_disc_data_idx"),
            models.Index(fields=("usuario", "concluida", "data"), name="aula_usuario_concl_data_idx"),
        ]

    def __str__(self):
        return self.titulo

    def clean(self):
        if self.disciplina_id and self.disciplina.usuario_id != self.usuario_id:
            raise ValidationError({"disciplina": "Selecione uma disciplina do seu perfil."})

    def save(self, *args, **kwargs):
        if self.status == StatusEstudo.CONCLUIDO:
            self.concluida = True
        super().save(*args, **kwargs)


class SessaoEstudo(OwnedModel):
    """Tempo de foco registrado pelo cronômetro global."""

    iniciada_em = models.DateTimeField("iniciada em")
    encerrada_em = models.DateTimeField("encerrada em")
    duracao_segundos = models.PositiveIntegerField("duração (segundos)")

    class Meta:
        ordering = ("-encerrada_em",)
        indexes = [
            models.Index(
                fields=("usuario", "iniciada_em"),
                name="sessao_usuario_inicio_idx",
            )
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duracao_segundos__gt=0),
                name="sessao_duracao_positiva",
            ),
            models.CheckConstraint(
                condition=models.Q(encerrada_em__gte=models.F("iniciada_em")),
                name="sessao_fim_apos_inicio",
            ),
        ]

    def __str__(self):
        return f"{self.usuario} · {self.duracao_segundos}s"
