from datetime import timedelta

from django.db.models import Q, Sum
from django.utils import timezone

from certificacoes.models import Certificacao
from competencias.selectors import competencias_do_usuario
from core.selectors import progresso_geral
from estudos.models import Aula
from objetivos.models import Objetivo
from projetos.models import Evidencia, Projeto, TarefaProjeto
from revisoes.models import AcaoRevisao, RevisaoPeriodica


def _primeiros_meses(quantidade=6):
    atual = timezone.localdate().replace(day=1)
    meses = []
    for _ in range(quantidade):
        meses.append(atual)
        atual = (atual - timedelta(days=1)).replace(day=1)
    return list(reversed(meses))


def horas_por_mes(usuario, quantidade=6):
    meses = _primeiros_meses(quantidade)
    totais = {mes: 0 for mes in meses}
    aulas = Aula.objects.filter(
        usuario=usuario,
        data__gte=meses[0],
    ).values_list("data", "duracao_estudada")
    for data, minutos in aulas:
        chave = data.replace(day=1)
        if chave in totais:
            totais[chave] += minutos
    maior = max(totais.values(), default=0)
    nomes = ("JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ")
    return [
        {
            "mes": nomes[data.month - 1],
            "ano": data.year,
            "minutos": minutos,
            "horas": round(minutos / 60, 1),
            "altura": max(4, round(minutos * 100 / maior)) if maior else 4,
        }
        for data, minutos in totais.items()
    ]


def distribuicao_objetivos(usuario):
    hoje = timezone.localdate()
    objetivos = Objetivo.objects.filter(
        usuario=usuario,
        arquivado_em__isnull=True,
    )
    grupos = [
        (
            "Em andamento",
            objetivos.filter(status=Objetivo.Status.EM_ANDAMENTO, prazo__gte=hoje).count()
            + objetivos.filter(status=Objetivo.Status.EM_ANDAMENTO, prazo__isnull=True).count(),
            "primary",
        ),
        (
            "Planejados",
            objetivos.filter(
                status__in=(Objetivo.Status.NAO_INICIADO, Objetivo.Status.PLANEJADO)
            )
            .filter(Q(prazo__gte=hoje) | Q(prazo__isnull=True))
            .count(),
            "info",
        ),
        (
            "Concluídos",
            objetivos.filter(status=Objetivo.Status.CONCLUIDO).count(),
            "success",
        ),
        (
            "Atrasados",
            objetivos.filter(prazo__lt=hoje).exclude(
                status__in=(Objetivo.Status.CONCLUIDO, Objetivo.Status.CANCELADO)
            ).count(),
            "danger",
        ),
    ]
    total = sum(valor for _, valor, _ in grupos)
    return [
        {
            "nome": nome,
            "valor": valor,
            "percentual": round(valor * 100 / total) if total else 0,
            "tom": tom,
        }
        for nome, valor, tom in grupos
    ]


def visao_indicadores(usuario):
    progresso = progresso_geral(usuario)
    projetos = Projeto.objects.filter(usuario=usuario, arquivado_em__isnull=True)
    tarefas = TarefaProjeto.objects.filter(usuario=usuario)
    total_tarefas = tarefas.count()
    tarefas_concluidas = tarefas.filter(
        status=TarefaProjeto.Status.CONCLUIDA
    ).count()
    competencias = list(
        competencias_do_usuario(usuario).filter(arquivado_em__isnull=True)
    )
    nivel_medio = (
        round(
            sum(item.ultima_avaliacao_nivel or 0 for item in competencias)
            / len(competencias),
            1,
        )
        if competencias
        else 0
    )
    meta_media = (
        round(sum(item.nivel_desejado for item in competencias) / len(competencias), 1)
        if competencias
        else 0
    )
    revisoes = RevisaoPeriodica.objects.filter(usuario=usuario)
    certificacoes = Certificacao.objects.filter(
        usuario=usuario, arquivado_em__isnull=True
    )
    total_revisoes = revisoes.count()
    revisoes_concluidas = revisoes.filter(
        status=RevisaoPeriodica.Status.CONCLUIDA
    ).count()
    total_certificacoes = certificacoes.count()
    certificacoes_aprovadas = certificacoes.filter(
        status=Certificacao.Status.APROVADA
    ).count()
    hoje = timezone.localdate()
    minutos_total = (
        Aula.objects.filter(usuario=usuario).aggregate(total=Sum("duracao_estudada"))[
            "total"
        ]
        or 0
    )
    acoes_atrasadas = (
        AcaoRevisao.objects.filter(usuario=usuario, prazo__lt=hoje)
        .exclude(
            status__in=(AcaoRevisao.Status.CONCLUIDA, AcaoRevisao.Status.CANCELADA)
        )
        .count()
    )
    return {
        "progresso": progresso,
        "meses_estudo": horas_por_mes(usuario),
        "objetivos_status": distribuicao_objetivos(usuario),
        "kpis": [
            {
                "rotulo": "Horas registradas",
                "valor": f"{round(minutos_total / 60, 1):g}h",
                "icone": "bi-clock-history",
            },
            {
                "rotulo": "Projetos ativos",
                "valor": projetos.exclude(
                    status__in=(Projeto.Status.CONCLUIDO, Projeto.Status.CANCELADO)
                ).count(),
                "icone": "bi-kanban",
            },
            {
                "rotulo": "Evidências",
                "valor": Evidencia.objects.filter(usuario=usuario).count(),
                "icone": "bi-patch-check",
            },
            {
                "rotulo": "Ações atrasadas",
                "valor": acoes_atrasadas,
                "icone": "bi-exclamation-triangle",
            },
        ],
        "projetos": {
            "total": projetos.count(),
            "tarefas": total_tarefas,
            "concluidas": tarefas_concluidas,
            "percentual": (
                round(tarefas_concluidas * 100 / total_tarefas)
                if total_tarefas
                else 0
            ),
        },
        "competencias": {
            "total": len(competencias),
            "nivel_medio": nivel_medio,
            "meta_media": meta_media,
            "percentual": (
                min(100, round(nivel_medio * 100 / meta_media)) if meta_media else 0
            ),
        },
        "revisoes": {
            "total": total_revisoes,
            "concluidas": revisoes_concluidas,
            "percentual": (
                round(revisoes_concluidas * 100 / total_revisoes)
                if total_revisoes
                else 0
            ),
        },
        "certificacoes": {
            "total": total_certificacoes,
            "aprovadas": certificacoes_aprovadas,
            "em_preparacao": certificacoes.filter(
                status__in=(
                    Certificacao.Status.PREPARANDO,
                    Certificacao.Status.AGENDADA,
                )
            ).count(),
            "percentual": (
                round(certificacoes_aprovadas * 100 / total_certificacoes)
                if total_certificacoes
                else 0
            ),
        },
    }
