import uuid

from django.core.exceptions import ValidationError
from django.db import models

from core.models import OwnedModel


def caminho_pdf_aula(instance, filename):
    return (
        f"usuarios/{instance.usuario_id}/aulas/{instance.aula_id}/"
        f"{uuid.uuid4().hex}.pdf"
    )


class MaterialPDF(OwnedModel):
    aula = models.ForeignKey(
        "estudos.Aula", on_delete=models.PROTECT, related_name="materiais_pdf"
    )
    titulo = models.CharField("título", max_length=180)
    descricao = models.TextField("descrição", blank=True)
    arquivo = models.FileField("arquivo", upload_to=caminho_pdf_aula)
    nome_original = models.CharField("nome original", max_length=255)
    tamanho = models.PositiveBigIntegerField("tamanho em bytes")
    sha256 = models.CharField("SHA-256", max_length=64)
    quantidade_paginas = models.PositiveIntegerField("quantidade de páginas")
    principal = models.BooleanField("PDF principal da aula", default=False)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("usuario", "aula"), name="material_usuario_aula_idx")
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("aula",),
                condition=models.Q(principal=True),
                name="um_pdf_principal_por_aula",
            )
        ]

    def __str__(self):
        return self.titulo

    def clean(self):
        if self.aula_id and self.aula.usuario_id != self.usuario_id:
            raise ValidationError({"aula": "Selecione uma aula do seu perfil."})
