from django.db.models import Count, Q

from .models import Projeto


def projetos_do_usuario(usuario):
    return (
        Projeto.objects.filter(usuario=usuario)
        .select_related("objetivo")
        .prefetch_related("tecnologias_vinculadas__tecnologia")
        .annotate(
            total_tarefas=Count("tarefas", distinct=True),
            tarefas_concluidas=Count(
                "tarefas",
                filter=Q(tarefas__status="concluida"),
                distinct=True,
            ),
            total_evidencias=Count("evidencias", distinct=True),
        )
    )
