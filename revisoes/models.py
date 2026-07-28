from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import OwnedModel


class RevisaoPeriodica(OwnedModel):
    class Tipo(models.TextChoices):
        SEMANAL = "semanal", "Semanal"
        MENSAL = "mensal", "Mensal"
        TRIMESTRAL = "trimestral", "Trimestral"
        ANUAL = "anual", "Anual"

    class Status(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        CONCLUIDA = "concluida", "Concluída"

    titulo = models.CharField("título", max_length=180)
    tipo = models.CharField("tipo", max_length=15, choices=Tipo.choices)
    periodo_inicio = models.DateField("início do período")
    periodo_fim = models.DateField("fim do período")
    status = models.CharField(
        "status", max_length=15, choices=Status.choices, default=Status.RASCUNHO
    )
    nota_periodo = models.PositiveSmallIntegerField(
        "nota do período", blank=True, null=True
    )
    conquistas = models.TextField("principais conquistas", blank=True)
    dificuldades = models.TextField("dificuldades e bloqueios", blank=True)
    aprendizados = models.TextField("aprendizados", blank=True)
    ajustes = models.TextField("o que ajustar no próximo ciclo", blank=True)
    conclusao = models.TextField("conclusão", blank=True)
    concluida_em = models.DateTimeField("concluída em", blank=True, null=True)

    class Meta:
        ordering = ("-periodo_fim", "-created_at")
        indexes = [
            models.Index(fields=("usuario", "status"), name="revisao_usuario_status_idx"),
            models.Index(fields=("usuario", "periodo_fim"), name="revisao_usuario_fim_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(nota_periodo__isnull=True)
                    | models.Q(nota_periodo__gte=1, nota_periodo__lte=5)
                ),
                name="revisao_nota_1_5",
            )
        ]

    def __str__(self):
        return self.titulo

    def clean(self):
        if self.periodo_fim < self.periodo_inicio:
            raise ValidationError(
                {"periodo_fim": "O fim do período não pode ser anterior ao início."}
            )

    def save(self, *args, **kwargs):
        if self.status == self.Status.CONCLUIDA:
            self.concluida_em = self.concluida_em or timezone.now()
        else:
            self.concluida_em = None
        super().save(*args, **kwargs)


class AcaoRevisao(OwnedModel):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        CONCLUIDA = "concluida", "Concluída"
        CANCELADA = "cancelada", "Cancelada"

    revisao = models.ForeignKey(
        RevisaoPeriodica, on_delete=models.CASCADE, related_name="acoes"
    )
    descricao = models.CharField("ação", max_length=240)
    prazo = models.DateField("prazo", blank=True, null=True)
    status = models.CharField(
        "status", max_length=20, choices=Status.choices, default=Status.PENDENTE
    )
    objetivo = models.ForeignKey(
        "objetivos.Objetivo",
        on_delete=models.PROTECT,
        related_name="acoes_revisao",
        blank=True,
        null=True,
    )
    projeto = models.ForeignKey(
        "projetos.Projeto",
        on_delete=models.PROTECT,
        related_name="acoes_revisao",
        blank=True,
        null=True,
    )
    competencia = models.ForeignKey(
        "competencias.Competencia",
        on_delete=models.PROTECT,
        related_name="acoes_revisao",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("status", "prazo", "created_at")
        indexes = [
            models.Index(fields=("usuario", "status", "prazo"), name="acao_revisao_prazo_idx")
        ]

    def __str__(self):
        return self.descricao

    def clean(self):
        relacionados = []
        for campo in ("revisao", "objetivo", "projeto", "competencia"):
            if getattr(self, f"{campo}_id", None):
                relacionados.append(getattr(self, campo))
        if any(item.usuario_id != self.usuario_id for item in relacionados):
            raise ValidationError("Todos os vínculos devem pertencer ao perfil pessoal.")
