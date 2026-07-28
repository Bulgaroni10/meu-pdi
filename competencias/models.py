from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import OwnedModel


class Competencia(OwnedModel):
    class Categoria(models.TextChoices):
        TECNICA = "tecnica", "Técnica"
        COMPORTAMENTAL = "comportamental", "Comportamental"
        NEGOCIO = "negocio", "Negócio"
        IDIOMA = "idioma", "Idioma"
        LIDERANCA = "lideranca", "Liderança"
        OUTRA = "outra", "Outra"

    nome = models.CharField("nome", max_length=120)
    categoria = models.CharField("categoria", max_length=20, choices=Categoria.choices)
    descricao = models.TextField("descrição", blank=True)
    nivel_desejado = models.PositiveSmallIntegerField("nível desejado", default=3)
    criterios = models.TextField(
        "critérios de evolução",
        blank=True,
        help_text="Descreva o que precisa demonstrar para avançar de nível.",
    )
    prazo = models.DateField("prazo", blank=True, null=True)
    arquivado_em = models.DateTimeField("arquivada em", blank=True, null=True)

    class Meta:
        ordering = ("categoria", "nome")
        indexes = [
            models.Index(
                fields=("usuario", "categoria"), name="competencia_usuario_cat_idx"
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("usuario", "nome"), name="competencia_usuario_nome_unico"
            ),
            models.CheckConstraint(
                condition=models.Q(nivel_desejado__gte=1, nivel_desejado__lte=5),
                name="competencia_nivel_desejado_1_5",
            ),
        ]

    def __str__(self):
        return self.nome

    @property
    def nivel_atual(self):
        if hasattr(self, "ultima_avaliacao_nivel"):
            return self.ultima_avaliacao_nivel or 0
        ultima = self.avaliacoes.order_by("-data", "-created_at").first()
        return ultima.nivel if ultima else 0

    @property
    def progresso(self):
        return (
            min(100, round(self.nivel_atual * 100 / self.nivel_desejado))
            if self.nivel_desejado
            else 0
        )


class AvaliacaoCompetencia(OwnedModel):
    competencia = models.ForeignKey(
        Competencia, on_delete=models.CASCADE, related_name="avaliacoes"
    )
    nivel = models.PositiveSmallIntegerField("nível demonstrado")
    justificativa = models.TextField("justificativa")
    data = models.DateField("data da avaliação", default=timezone.localdate)
    evidencias = models.ManyToManyField(
        "projetos.Evidencia",
        through="EvidenciaCompetencia",
        related_name="avaliacoes_competencia",
    )

    class Meta:
        ordering = ("-data", "-created_at")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(nivel__gte=1, nivel__lte=5),
                name="avaliacao_nivel_1_5",
            )
        ]

    def __str__(self):
        return f"{self.competencia} — nível {self.nivel}"

    def clean(self):
        if self.competencia_id and self.competencia.usuario_id != self.usuario_id:
            raise ValidationError({"competencia": "Selecione uma competência do seu perfil."})


class EvidenciaCompetencia(OwnedModel):
    avaliacao = models.ForeignKey(
        AvaliacaoCompetencia,
        on_delete=models.CASCADE,
        related_name="vinculos_evidencia",
    )
    evidencia = models.ForeignKey(
        "projetos.Evidencia",
        on_delete=models.PROTECT,
        related_name="vinculos_competencia",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("avaliacao", "evidencia"),
                name="avaliacao_evidencia_unica",
            )
        ]

    def clean(self):
        if self.avaliacao_id and self.avaliacao.usuario_id != self.usuario_id:
            raise ValidationError("A avaliação deve pertencer ao perfil pessoal.")
        if self.evidencia_id and self.evidencia.usuario_id != self.usuario_id:
            raise ValidationError("A evidência deve pertencer ao perfil pessoal.")
