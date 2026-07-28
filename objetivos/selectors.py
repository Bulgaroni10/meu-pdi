from datetime import timedelta

from django.db.models import Q, QuerySet
from django.utils import timezone

from .models import Objetivo


STATUS_FINALIZADOS = (Objetivo.Status.CONCLUIDO, Objetivo.Status.CANCELADO)


def objetivos_do_usuario(usuario) -> QuerySet[Objetivo]:
    return Objetivo.objects.filter(usuario=usuario).prefetch_related("tags")


def objetivos_filtrados(usuario, filtros: dict) -> QuerySet[Objetivo]:
    hoje = timezone.localdate()
    queryset = objetivos_do_usuario(usuario)

    if not filtros.get("arquivados"):
        queryset = queryset.filter(arquivado_em__isnull=True)

    if termo := filtros.get("q"):
        queryset = queryset.filter(
            Q(titulo__icontains=termo)
            | Q(descricao__icontains=termo)
            | Q(proxima_acao__icontains=termo)
            | Q(tags__nome__icontains=termo)
        ).distinct()

    status = filtros.get("status")
    if status == Objetivo.Status.ATRASADO:
        queryset = queryset.filter(prazo__lt=hoje).exclude(status__in=STATUS_FINALIZADOS)
    elif status:
        queryset = queryset.filter(status=status)

    if categoria := filtros.get("categoria"):
        queryset = queryset.filter(categoria=categoria)
    if prioridade := filtros.get("prioridade"):
        queryset = queryset.filter(prioridade=prioridade)

    prazo = filtros.get("prazo")
    if prazo == "proximos_30":
        queryset = queryset.filter(prazo__range=(hoje, hoje + timedelta(days=30)))
    elif prazo == "atrasados":
        queryset = queryset.filter(prazo__lt=hoje).exclude(status__in=STATUS_FINALIZADOS)
    elif prazo == "sem_prazo":
        queryset = queryset.filter(prazo__isnull=True)

    ordenacao = filtros.get("ordenacao") or "-updated_at"
    permitidas = {"-updated_at", "prazo", "-prioridade", "titulo", "-progresso"}
    return queryset.order_by(ordenacao if ordenacao in permitidas else "-updated_at")


def resumo_objetivos(usuario) -> dict:
    hoje = timezone.localdate()
    ativos = objetivos_do_usuario(usuario).filter(arquivado_em__isnull=True)
    atrasados = ativos.filter(prazo__lt=hoje).exclude(status__in=STATUS_FINALIZADOS)
    concluidos = ativos.filter(status=Objetivo.Status.CONCLUIDO)
    progresso_medio = 0
    if ativos.exists():
        total = sum(ativos.values_list("progresso", flat=True))
        progresso_medio = round(total / ativos.count())
    return {
        "total": ativos.count(),
        "ativos": ativos.exclude(status__in=STATUS_FINALIZADOS).count(),
        "atrasados": atrasados.count(),
        "concluidos": concluidos.count(),
        "progresso_medio": progresso_medio,
    }
