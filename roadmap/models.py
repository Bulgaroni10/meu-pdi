import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg
from django.utils import timezone

from core.models import OwnedModel


def caminho_pdf_roadmap(instance, filename: str) -> str:
    return (
        f"usuarios/{instance.usuario_id}/roadmaps/fontes/"
        f"{uuid.uuid4().hex}{Path(filename).suffix.lower()}"
    )


class FonteRoadmap(OwnedModel):
    arquivo = models.FileField("arquivo PDF", upload_to=caminho_pdf_roadmap)
    nome_original = models.CharField("nome original", max_length=255)
    mime_type = models.CharField("MIME type", max_length=80, default="application/pdf")
    tamanho = models.PositiveBigIntegerField("tamanho em bytes")
    sha256 = models.CharField("SHA-256", max_length=64)
    quantidade_paginas = models.PositiveIntegerField("quantidade de páginas")
    titulo_extraido = models.CharField("título extraído", max_length=240, blank=True)
    extraido_em = models.DateTimeField("extraído em", auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=("usuario", "sha256"),
                name="fonte_roadmap_hash_idx",
            )
        ]

    def __str__(self) -> str:
        return self.nome_original


class Roadmap(OwnedModel):
    class Status(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        PLANEJADO = "planejado", "Planejado"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        PAUSADO = "pausado", "Pausado"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"

    class Prioridade(models.TextChoices):
        BAIXA = "baixa", "Baixa"
        MEDIA = "media", "Média"
        ALTA = "alta", "Alta"
        CRITICA = "critica", "Crítica"

    nome = models.CharField("nome", max_length=180)
    descricao = models.TextField("descrição", blank=True)
    objetivo = models.ForeignKey(
        "objetivos.Objetivo",
        on_delete=models.PROTECT,
        related_name="roadmaps",
        blank=True,
        null=True,
    )
    fonte_pdf = models.OneToOneField(
        FonteRoadmap,
        on_delete=models.SET_NULL,
        related_name="roadmap",
        blank=True,
        null=True,
    )
    data_inicio = models.DateField("data de início", default=timezone.localdate)
    prazo = models.DateField("prazo final", blank=True, null=True)
    status = models.CharField(
        "status",
        max_length=20,
        choices=Status.choices,
        default=Status.RASCUNHO,
    )
    prioridade = models.CharField(
        "prioridade",
        max_length=10,
        choices=Prioridade.choices,
        default=Prioridade.MEDIA,
    )
    progresso_manual = models.PositiveSmallIntegerField(
        "progresso manual",
        blank=True,
        null=True,
        help_text="Deixe vazio para calcular pelas fases.",
    )
    observacoes = models.TextField("observações", blank=True)
    gerado_de_pdf = models.BooleanField("gerado de PDF", default=False)
    arquivado_em = models.DateTimeField("arquivado em", blank=True, null=True)

    class Meta:
        ordering = ("-updated_at",)
        indexes = [
            models.Index(
                fields=("usuario", "status"),
                name="roadmap_usuario_status_idx",
            ),
            models.Index(
                fields=("usuario", "prazo"),
                name="roadmap_usuario_prazo_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(progresso_manual__isnull=True)
                    | models.Q(progresso_manual__gte=0, progresso_manual__lte=100)
                ),
                name="roadmap_progresso_entre_0_100",
            )
        ]

    def __str__(self) -> str:
        return self.nome

    def clean(self):
        super().clean()
        if self.objetivo_id and self.objetivo.usuario_id != self.usuario_id:
            raise ValidationError(
                {"objetivo": "O objetivo deve pertencer ao perfil pessoal."}
            )
        if self.prazo and self.data_inicio and self.prazo < self.data_inicio:
            raise ValidationError(
                {"prazo": "O prazo não pode ser anterior à data de início."}
            )

    @property
    def progresso(self) -> int:
        if self.progresso_manual is not None:
            return self.progresso_manual
        if hasattr(self, "media_fases"):
            return round(self.media_fases or 0)
        media = self.fases.aggregate(media=Avg("progresso"))["media"]
        return round(media or 0)

    @property
    def observacoes_publicas(self) -> str:
        return self.observacoes.replace(
            "seed:pdi-infra-cloud-gratuito-v1", ""
        ).strip()


class FaseRoadmap(OwnedModel):
    class Status(models.TextChoices):
        NAO_INICIADA = "nao_iniciada", "Não iniciada"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        BLOQUEADA = "bloqueada", "Bloqueada"
        CONCLUIDA = "concluida", "Concluída"

    roadmap = models.ForeignKey(
        Roadmap,
        on_delete=models.CASCADE,
        related_name="fases",
    )
    titulo = models.CharField("título", max_length=180)
    descricao = models.TextField("descrição", blank=True)
    ordem = models.PositiveSmallIntegerField("ordem")
    data_prevista_inicio = models.DateField("início previsto", blank=True, null=True)
    data_prevista_conclusao = models.DateField(
        "conclusão prevista", blank=True, null=True
    )
    data_real_conclusao = models.DateField(
        "conclusão real", blank=True, null=True
    )
    status = models.CharField(
        "status",
        max_length=20,
        choices=Status.choices,
        default=Status.NAO_INICIADA,
    )
    progresso = models.PositiveSmallIntegerField("progresso", default=0)
    criterios_conclusao = models.TextField("critérios de conclusão", blank=True)
    dependencias = models.TextField("dependências", blank=True)
    proxima_acao = models.CharField("próxima ação", max_length=240, blank=True)

    class Meta:
        ordering = ("ordem",)
        constraints = [
            models.UniqueConstraint(
                fields=("roadmap", "ordem"),
                name="fase_roadmap_ordem_unica",
            ),
            models.CheckConstraint(
                condition=models.Q(progresso__gte=0, progresso__lte=100),
                name="fase_progresso_entre_0_100",
            ),
        ]

    def __str__(self) -> str:
        return self.titulo

    def clean(self):
        super().clean()
        if self.roadmap_id and self.roadmap.usuario_id != self.usuario_id:
            raise ValidationError("A fase deve pertencer ao mesmo perfil do roadmap.")
        if (
            self.data_prevista_inicio
            and self.data_prevista_conclusao
            and self.data_prevista_conclusao < self.data_prevista_inicio
        ):
            raise ValidationError(
                {
                    "data_prevista_conclusao": (
                        "A conclusão não pode ser anterior ao início."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if self.status == self.Status.CONCLUIDA:
            self.progresso = 100
            self.data_real_conclusao = (
                self.data_real_conclusao or timezone.localdate()
            )
        super().save(*args, **kwargs)


class EtapaRoadmap(OwnedModel):
    fase = models.ForeignKey(
        FaseRoadmap,
        on_delete=models.CASCADE,
        related_name="etapas",
    )
    titulo = models.CharField("título", max_length=180)
    descricao = models.TextField("descrição", blank=True)
    ordem = models.PositiveSmallIntegerField("ordem")
    concluida = models.BooleanField("concluída", default=False)

    class Meta:
        ordering = ("ordem",)
        constraints = [
            models.UniqueConstraint(
                fields=("fase", "ordem"),
                name="etapa_fase_ordem_unica",
            )
        ]

    def __str__(self) -> str:
        return self.titulo


class EntregaRoadmap(OwnedModel):
    fase = models.ForeignKey(
        FaseRoadmap,
        on_delete=models.CASCADE,
        related_name="entregas",
    )
    titulo = models.CharField("título", max_length=180)
    descricao = models.TextField("descrição", blank=True)
    criterio_aceite = models.TextField("critério de aceite", blank=True)
    concluida = models.BooleanField("concluída", default=False)

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return self.titulo
