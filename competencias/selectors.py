from django.db.models import OuterRef, Subquery

from .models import AvaliacaoCompetencia, Competencia


def competencias_do_usuario(usuario):
    ultima_avaliacao = AvaliacaoCompetencia.objects.filter(
        competencia=OuterRef("pk")
    ).order_by("-data", "-created_at")
    return Competencia.objects.filter(usuario=usuario).annotate(
        ultima_avaliacao_nivel=Subquery(ultima_avaliacao.values("nivel")[:1])
    )
