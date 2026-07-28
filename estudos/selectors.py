from django.db.models import Count, Q

from .models import Aula, Curso, Disciplina, Trilha


def resumo_estudos(usuario):
    return {
        "trilhas": Trilha.objects.filter(usuario=usuario).count(),
        "cursos": Curso.objects.filter(usuario=usuario).count(),
        "disciplinas": Disciplina.objects.filter(usuario=usuario).count(),
        "aulas": Aula.objects.filter(usuario=usuario).count(),
        "concluidas": Aula.objects.filter(usuario=usuario, concluida=True).count(),
    }


def cursos_do_usuario(usuario):
    return Curso.objects.filter(usuario=usuario).prefetch_related(
        "trilhas", "periodos", "disciplinas"
    )


def disciplinas_do_usuario(usuario):
    return Disciplina.objects.filter(usuario=usuario).select_related("curso", "periodo").annotate(
        total_aulas=Count("aulas"),
        aulas_concluidas=Count("aulas", filter=Q(aulas__concluida=True)),
    )
