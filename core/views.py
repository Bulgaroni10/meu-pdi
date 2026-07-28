from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from competencias.models import Competencia
from objetivos.models import Objetivo
from objetivos.selectors import objetivos_do_usuario, resumo_objetivos

from .selectors import (
    atividades_recentes,
    evidencias_recentes,
    progresso_geral,
    proximos_prazos,
    ritmo_estudos,
)
from .search import buscar_tudo


def dashboard(request):
    """Dashboard pessoal consolidado com dados reais do PDI."""
    resumo = resumo_objetivos(request.user)
    objetivos_ativos = (
        objetivos_do_usuario(request.user)
        .filter(arquivado_em__isnull=True)
        .exclude(status__in=(Objetivo.Status.CONCLUIDO, Objetivo.Status.CANCELADO))
    )
    objetivo_principal = objetivos_ativos.filter(
        status=Objetivo.Status.EM_ANDAMENTO
    ).first() or objetivos_ativos.first()
    progresso = progresso_geral(request.user)
    semanas = ritmo_estudos(request.user)
    horas_semana = semanas[-1]["horas"]
    prazos = proximos_prazos(request.user)
    hoje = timezone.localdate()
    periodo_pdi = None
    if objetivo_principal and objetivo_principal.prazo:
        total_dias = max(
            1, (objetivo_principal.prazo - objetivo_principal.data_inicio).days
        )
        dias_decorridos = max(
            0, min(total_dias, (hoje - objetivo_principal.data_inicio).days)
        )
        dias_restantes = max(0, (objetivo_principal.prazo - hoje).days)
        periodo_pdi = {
            "inicio": objetivo_principal.data_inicio,
            "fim": objetivo_principal.prazo,
            "decorrido": _periodo_legivel(dias_decorridos),
            "restante": _periodo_legivel(dias_restantes),
            "percentual": round(dias_decorridos * 100 / total_dias),
        }
    context = {
        "titulo_pagina": "Dashboard",
        "resumo_objetivos": resumo,
        "objetivo_principal": objetivo_principal,
        "progresso_geral": progresso,
        "semanas_estudo": semanas,
        "proximos_prazos": prazos,
        "atividades_recentes": atividades_recentes(request.user),
        "evidencias_recentes": evidencias_recentes(request.user),
        "competencias_destaque": Competencia.objects.filter(
            usuario=request.user,
            arquivado_em__isnull=True,
        )[:5],
        "periodo_pdi": periodo_pdi,
        "kpis": [
            {
                "rotulo": "Progresso geral",
                "valor": f"{progresso['valor']}%",
                "icone": "bi-graph-up-arrow",
                "tom": "primary",
            },
            {
                "rotulo": "Horas na semana",
                "valor": f"{horas_semana:g}h",
                "icone": "bi-clock-history",
                "tom": "info",
            },
            {
                "rotulo": "Cobertura do cálculo",
                "valor": f"{progresso['cobertura']}%",
                "icone": "bi-pie-chart",
                "tom": "warning",
            },
            {
                "rotulo": "Prazos acompanhados",
                "valor": str(len(prazos)),
                "icone": "bi-calendar-check",
                "tom": "danger",
            },
        ],
    }
    return render(request, "core/dashboard.html", context)


def _periodo_legivel(dias):
    anos, resto = divmod(max(0, dias), 365)
    meses, dias = divmod(resto, 30)
    partes = []
    if anos:
        partes.append(f"{anos}a")
    if meses or anos:
        partes.append(f"{meses}m")
    partes.append(f"{dias}d")
    return " ".join(partes)


def busca(request):
    termo = request.GET.get("q", "").strip()
    grupos = buscar_tudo(request.user, termo)
    return render(
        request,
        "core/busca.html",
        {
            "termo": termo,
            "grupos": grupos,
            "total_resultados": sum(len(grupo["itens"]) for grupo in grupos),
        },
    )


def health_live(request):
    return JsonResponse({"status": "ok", "service": "meu-pdi"})


def health_ready(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse(
            {"status": "unavailable", "database": "error"},
            status=503,
        )
    return JsonResponse({"status": "ok", "database": "connected"})
