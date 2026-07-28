from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import OwnedModel, TimeStampedModel, UUIDModel


class Tag(OwnedModel):
    nome = models.CharField("nome", max_length=40)
    slug = models.SlugField("slug", max_length=50)

    class Meta:
        ordering = ("nome",)
        constraints = [
            models.UniqueConstraint(
                fields=("usuario", "slug"),
                name="objetivos_tag_usuario_slug_unico",
            )
        ]

    def __str__(self) -> str:
        return self.nome


class Objetivo(OwnedModel):
    class Categoria(models.TextChoices):
        PROFISSIONAL = "profissional", "Profissional"
        ACADEMICO = "academico", "Acadêmico"
        PESSOAL = "pessoal", "Pessoal"
        FINANCEIRO = "financeiro", "Financeiro"
        SAUDE = "saude", "Saúde"
        COMUNICACAO = "comunicacao", "Comunicação"
        OUTRO = "outro", "Outro"

    class Prioridade(models.TextChoices):
        BAIXA = "baixa", "Baixa"
        MEDIA = "media", "Média"
        ALTA = "alta", "Alta"
        CRITICA = "critica", "Crítica"

    class Status(models.TextChoices):
        NAO_INICIADO = "nao_iniciado", "Não iniciado"
        PLANEJADO = "planejado", "Planejado"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        PAUSADO = "pausado", "Pausado"
        ATRASADO = "atrasado", "Atrasado"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"

    titulo = models.CharField("título", max_length=180)
    descricao = models.TextField("descrição", blank=True)
    categoria = models.CharField(
        "categoria",
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.PROFISSIONAL,
    )
    motivo = models.TextField("por que este objetivo importa?", blank=True)
    data_inicio = models.DateField("data de início", default=timezone.localdate)
    prazo = models.DateField("prazo", blank=True, null=True)
    prioridade = models.CharField(
        "prioridade",
        max_length=10,
        choices=Prioridade.choices,
        default=Prioridade.MEDIA,
    )
    status = models.CharField(
        "status",
        max_length=20,
        choices=Status.choices,
        default=Status.NAO_INICIADO,
    )
    progresso = models.PositiveSmallIntegerField("progresso", default=0)
    resultado_esperado = models.TextField("resultado esperado", blank=True)
    evidencia_esperada = models.TextField("evidência esperada", blank=True)
    proxima_acao = models.CharField("próxima ação", max_length=240, blank=True)
    obstaculos = models.TextField("obstáculos", blank=True)
    observacoes = models.TextField("observações", blank=True)
    tags = models.ManyToManyField(Tag, verbose_name="tags", blank=True)
    data_conclusao = models.DateField(
        "data de conclusão", blank=True, null=True, editable=False
    )
    arquivado_em = models.DateTimeField("arquivado em", blank=True, null=True)

    class Meta:
        ordering = ("-updated_at",)
        indexes = [
            models.Index(
                fields=("usuario", "status"),
                name="objetivo_usuario_status_idx",
            ),
            models.Index(
                fields=("usuario", "prazo"),
                name="objetivo_usuario_prazo_idx",
            ),
            models.Index(
                fields=("usuario", "status", "prazo"),
                name="objetivo_status_prazo_idx",
            ),
            models.Index(
                fields=("usuario", "updated_at"),
                name="objetivo_usuario_atual_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(progresso__gte=0, progresso__lte=100),
                name="objetivo_progresso_entre_0_100",
            )
        ]

    def __str__(self) -> str:
        return self.titulo

    def clean(self):
        super().clean()
        if self.prazo and self.data_inicio and self.prazo < self.data_inicio:
            raise ValidationError(
                {"prazo": "O prazo não pode ser anterior à data de início."}
            )

    def save(self, *args, **kwargs):
        if self.status == self.Status.CONCLUIDO:
            self.progresso = 100
            self.data_conclusao = self.data_conclusao or timezone.localdate()
        else:
            self.data_conclusao = None
        super().save(*args, **kwargs)

    @property
    def is_atrasado(self) -> bool:
        if not self.prazo or self.arquivado_em:
            return False
        finalizados = {self.Status.CONCLUIDO, self.Status.CANCELADO}
        return self.status not in finalizados and self.prazo < timezone.localdate()

    @property
    def status_efetivo(self) -> str:
        return self.Status.ATRASADO if self.is_atrasado else self.status

    @property
    def status_efetivo_label(self) -> str:
        return dict(self.Status.choices)[self.status_efetivo]

    @property
    def dias_restantes(self) -> int | None:
        if not self.prazo:
            return None
        return (self.prazo - timezone.localdate()).days

    @property
    def is_arquivado(self) -> bool:
        return self.arquivado_em is not None


class HistoricoObjetivo(UUIDModel, TimeStampedModel):
    class Tipo(models.TextChoices):
        CRIACAO = "criacao", "Criação"
        ALTERACAO = "alteracao", "Alteração"
        ARQUIVAMENTO = "arquivamento", "Arquivamento"
        RESTAURACAO = "restauracao", "Restauração"

    objetivo = models.ForeignKey(
        Objetivo,
        on_delete=models.CASCADE,
        related_name="historico",
    )
    usuario = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.PROTECT,
        related_name="historicos_objetivos",
    )
    tipo = models.CharField("tipo", max_length=20, choices=Tipo.choices)
    campo = models.CharField("campo", max_length=50, blank=True)
    valor_anterior = models.TextField("valor anterior", blank=True)
    valor_novo = models.TextField("valor novo", blank=True)
    descricao = models.CharField("descrição", max_length=240)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=("objetivo", "created_at"),
                name="historico_objetivo_data_idx",
            )
        ]

    def __str__(self) -> str:
        return self.descricao
