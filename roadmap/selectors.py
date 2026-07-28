from django.db.models import Avg, QuerySet

from .models import Roadmap


def roadmaps_do_usuario(usuario) -> QuerySet[Roadmap]:
    return (
        Roadmap.objects.filter(usuario=usuario, arquivado_em__isnull=True)
        .annotate(media_fases=Avg("fases__progresso"))
        .select_related("objetivo", "fonte_pdf")
        .prefetch_related("fases__etapas", "fases__entregas")
    )
