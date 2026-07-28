from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import OwnedModel


class Certificacao(OwnedModel):
    class Status(models.TextChoices):
        PLANEJADA = "planejada", "Planejada"
        PREPARANDO = "preparando", "Em preparação"
        AGENDADA = "agendada", "Prova agendada"
        APROVADA = "aprovada", "Aprovada"
        REPROVADA = "reprovada", "Reprovada"
        EXPIRADA = "expirada", "Expirada"
        CANCELADA = "cancelada", "Cancelada"

    class Prioridade(models.TextChoices):
        BAIXA = "baixa", "Baixa"
        MEDIA = "media", "Média"
        ALTA = "alta", "Alta"

    nome = models.CharField("certificação", max_length=180)
    instituicao = models.CharField("instituição", max_length=140)
    codigo = models.CharField("código", max_length=50, blank=True)
    status = models.CharField(
        "status", max_length=20, choices=Status.choices, default=Status.PLANEJADA
    )
    prioridade = models.CharField(
        "prioridade",
        max_length=10,
        choices=Prioridade.choices,
        default=Prioridade.MEDIA,
    )
    progresso = models.PositiveSmallIntegerField("progresso da preparação", default=0)
    data_inicio = models.DateField("início da preparação", default=timezone.localdate)
    data_prova = models.DateField("data da prova", blank=True, null=True)
    data_resultado = models.DateField("data do resultado", blank=True, null=True)
    data_validade = models.DateField("validade até", blank=True, null=True)
    custo_previsto = models.DecimalField(
        "custo previsto", max_digits=10, decimal_places=2, default=0
    )
    custo_real = models.DecimalField(
        "custo real", max_digits=10, decimal_places=2, blank=True, null=True
    )
    nota = models.DecimalField(
        "nota obtida", max_digits=7, decimal_places=2, blank=True, null=True
    )
    objetivo = models.ForeignKey(
        "objetivos.Objetivo",
        on_delete=models.PROTECT,
        related_name="certificacoes",
        blank=True,
        null=True,
    )
    trilha = models.ForeignKey(
        "estudos.Trilha",
        on_delete=models.PROTECT,
        related_name="certificacoes",
        blank=True,
        null=True,
    )
    certificado = models.ForeignKey(
        "biblioteca.MaterialPDF",
        on_delete=models.SET_NULL,
        related_name="certificacoes",
        blank=True,
        null=True,
    )
    url_oficial = models.URLField("página oficial", blank=True)
    url_agendamento = models.URLField("página de agendamento", blank=True)
    observacoes = models.TextField("observações", blank=True)
    arquivado_em = models.DateTimeField("arquivada em", blank=True, null=True)

    class Meta:
        ordering = ("data_prova", "-prioridade", "nome")
        indexes = [
            models.Index(fields=("usuario", "status"), name="cert_usuario_status_idx"),
            models.Index(fields=("usuario", "data_prova"), name="cert_usuario_prova_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(progresso__gte=0, progresso__lte=100),
                name="certificacao_progresso_0_100",
            )
        ]

    def __str__(self):
        return f"{self.codigo} — {self.nome}" if self.codigo else self.nome

    def clean(self):
        relacionados = []
        for campo in ("objetivo", "trilha", "certificado"):
            if getattr(self, f"{campo}_id", None):
                relacionados.append(getattr(self, campo))
        if any(item.usuario_id != self.usuario_id for item in relacionados):
            raise ValidationError("Todos os vínculos devem pertencer ao perfil pessoal.")
        if self.data_prova and self.data_prova < self.data_inicio:
            raise ValidationError(
                {"data_prova": "A prova não pode ser anterior ao início da preparação."}
            )
        if self.data_resultado and not self.data_prova:
            raise ValidationError(
                {"data_resultado": "Informe a data da prova antes do resultado."}
            )
        if self.status in (self.Status.APROVADA, self.Status.REPROVADA) and not self.data_prova:
            raise ValidationError(
                {"data_prova": "Informe a data da prova para registrar o resultado."}
            )

    def save(self, *args, **kwargs):
        if self.status == self.Status.APROVADA:
            self.progresso = 100
            self.data_resultado = self.data_resultado or timezone.localdate()
        super().save(*args, **kwargs)

    @property
    def dias_ate_prova(self):
        if not self.data_prova:
            return None
        return (self.data_prova - timezone.localdate()).days
