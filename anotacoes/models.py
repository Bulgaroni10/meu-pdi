from django.core.exceptions import ValidationError
from django.db import models

from core.models import OwnedModel


class Anotacao(OwnedModel):
    class Tipo(models.TextChoices):
        GERAL = "geral", "Anotação geral"
        RESUMO = "resumo", "Resumo"
        DUVIDA = "duvida", "Dúvida"
        CONCEITO = "conceito", "Conceito importante"
        EXERCICIO = "exercicio", "Exercício"
        PRATICA = "pratica", "Aplicação prática"
        IDEIA = "ideia", "Ideia de projeto"
        REVISAO = "revisao", "Revisão"
        CODIGO = "codigo", "Bloco de código"

    aula = models.ForeignKey(
        "estudos.Aula", on_delete=models.PROTECT, related_name="anotacoes"
    )
    titulo = models.CharField("título", max_length=180)
    conteudo_html = models.TextField("conteúdo", blank=True)
    conteudo_texto = models.TextField("texto pesquisável", blank=True)
    tipo = models.CharField("tipo", max_length=20, choices=Tipo.choices, default=Tipo.GERAL)
    pagina_pdf = models.PositiveIntegerField("página do PDF", blank=True, null=True)
    trecho_referencia = models.TextField("trecho de referência", blank=True)
    favorita = models.BooleanField("favorita", default=False)
    tags = models.CharField("tags", max_length=240, blank=True)
    versao_atual = models.PositiveIntegerField("versão atual", default=1)

    class Meta:
        ordering = ("-updated_at",)
        indexes = [
            models.Index(fields=("usuario", "aula", "updated_at"), name="anotacao_aula_data_idx")
        ]

    def __str__(self):
        return self.titulo

    def clean(self):
        if self.aula_id and self.aula.usuario_id != self.usuario_id:
            raise ValidationError({"aula": "Selecione uma aula do seu perfil."})


class VersaoAnotacao(OwnedModel):
    anotacao = models.ForeignKey(
        Anotacao, on_delete=models.CASCADE, related_name="versoes"
    )
    numero = models.PositiveIntegerField("número")
    titulo = models.CharField("título", max_length=180)
    conteudo_html = models.TextField("conteúdo")
    conteudo_texto = models.TextField("texto", blank=True)

    class Meta:
        ordering = ("-numero",)
        constraints = [
            models.UniqueConstraint(
                fields=("anotacao", "numero"), name="versao_anotacao_numero_unico"
            )
        ]

    def __str__(self):
        return f"{self.anotacao} - versão {self.numero}"
