from datetime import timedelta

from django.db.models import Avg, Sum
from django.db.models.functions import TruncDate
from django.urls import reverse
from django.utils import timezone

from anotacoes.models import Anotacao
from certificacoes.models import Certificacao
from competencias.models import Competencia
from competencias.selectors import competencias_do_usuario
from estudos.models import Aula, SessaoEstudo, Trilha
from objetivos.models import Objetivo
from projetos.models import Evidencia, Projeto
from revisoes.models import AcaoRevisao, RevisaoPeriodica
from roadmap.models import Roadmap


STATUS_FINAIS_OBJETIVO = (Objetivo.Status.CONCLUIDO, Objetivo.Status.CANCELADO)
STATUS_FINAIS_ROADMAP = (Roadmap.Status.CONCLUIDO, Roadmap.Status.CANCELADO)
STATUS_FINAIS_PROJETO = (Projeto.Status.CONCLUIDO, Projeto.Status.CANCELADO)


def progresso_geral(usuario) -> dict:
    """Calcula a evolução usando somente domínios que já possuem dados."""
    componentes = []

    objetivos = Objetivo.objects.filter(usuario=usuario, arquivado_em__isnull=True)
    if objetivos.exists():
        componentes.append(
            {
                "nome": "Objetivos",
                "peso": 25,
                "valor": round(objetivos.aggregate(media=Avg("progresso"))["media"] or 0),
            }
        )

    trilhas = Trilha.objects.filter(usuario=usuario)
    if trilhas.exists():
        componentes.append(
            {
                "nome": "Trilhas",
                "peso": 20,
                "valor": round(trilhas.aggregate(media=Avg("progresso"))["media"] or 0),
            }
        )

    aulas = Aula.objects.filter(usuario=usuario)
    if aulas.exists():
        total = aulas.count()
        componentes.append(
            {
                "nome": "Aulas",
                "peso": 15,
                "valor": round(aulas.filter(concluida=True).count() * 100 / total),
            }
        )

    projetos = Projeto.objects.filter(usuario=usuario, arquivado_em__isnull=True)
    if projetos.exists():
        componentes.append(
            {
                "nome": "Projetos",
                "peso": 20,
                "valor": round(projetos.aggregate(media=Avg("progresso"))["media"] or 0),
            }
        )

    competencias = competencias_do_usuario(usuario).filter(arquivado_em__isnull=True)
    if competencias.exists():
        valores = [
            min(100, round((item.ultima_avaliacao_nivel or 0) * 100 / item.nivel_desejado))
            for item in competencias
        ]
        componentes.append(
            {
                "nome": "Competências",
                "peso": 10,
                "valor": round(sum(valores) / len(valores)),
            }
        )

    revisoes = RevisaoPeriodica.objects.filter(usuario=usuario)
    if revisoes.exists():
        componentes.append(
            {
                "nome": "Revisões",
                "peso": 10,
                "valor": round(
                    revisoes.filter(status=RevisaoPeriodica.Status.CONCLUIDA).count()
                    * 100
                    / revisoes.count()
                ),
            }
        )

    peso_com_dados = sum(item["peso"] for item in componentes)
    valor = (
        round(
            sum(item["valor"] * item["peso"] for item in componentes)
            / peso_com_dados
        )
        if peso_com_dados
        else 0
    )
    return {
        "valor": valor,
        "cobertura": peso_com_dados,
        "componentes": componentes,
    }


def ritmo_estudos(usuario, quantidade_semanas=8) -> list[dict]:
    hoje = timezone.localdate()
    inicio_semana_atual = hoje - timedelta(days=hoje.weekday())
    primeiro_dia = inicio_semana_atual - timedelta(weeks=quantidade_semanas - 1)
    totais = {primeiro_dia + timedelta(weeks=i): 0 for i in range(quantidade_semanas)}

    aulas = Aula.objects.filter(
        usuario=usuario,
        data__range=(primeiro_dia, hoje),
    ).values_list("data", "duracao_estudada")
    for data, minutos in aulas:
        inicio = data - timedelta(days=data.weekday())
        totais[inicio] += minutos * 60

    sessoes = (
        SessaoEstudo.objects.filter(
            usuario=usuario,
            iniciada_em__date__range=(primeiro_dia, hoje),
        )
        .annotate(data=TruncDate("iniciada_em"))
        .values("data")
        .annotate(total=Sum("duracao_segundos"))
    )
    for sessao in sessoes:
        data = sessao["data"]
        inicio = data - timedelta(days=data.weekday())
        totais[inicio] += sessao["total"]

    maior_total = max(totais.values(), default=0)
    semanas = []
    for inicio, segundos in totais.items():
        minutos = round(segundos / 60)
        horas = round(segundos / 3600, 1)
        altura = round(segundos * 100 / maior_total) if maior_total else 0
        semanas.append(
            {
                "inicio": inicio,
                "fim": inicio + timedelta(days=6),
                "rotulo": inicio.strftime("%d/%m"),
                "minutos": minutos,
                "horas": horas,
                "altura": max(altura, 6) if minutos else 3,
            }
        )
    return semanas


def proximos_prazos(usuario, limite=5) -> list[dict]:
    hoje = timezone.localdate()
    itens = []
    objetivos = (
        Objetivo.objects.filter(
            usuario=usuario,
            arquivado_em__isnull=True,
            prazo__isnull=False,
        )
        .exclude(status__in=STATUS_FINAIS_OBJETIVO)
        .only("id", "titulo", "prazo")
    )
    for objetivo in objetivos:
        itens.append(
            {
                "titulo": objetivo.titulo,
                "tipo": "Objetivo",
                "prazo": objetivo.prazo,
                "dias": (objetivo.prazo - hoje).days,
                "url": reverse("objetivos:detalhe", args=[objetivo.id]),
                "icone": "bi-bullseye",
            }
        )

    roadmaps = (
        Roadmap.objects.filter(
            usuario=usuario,
            arquivado_em__isnull=True,
            prazo__isnull=False,
        )
        .exclude(status__in=STATUS_FINAIS_ROADMAP)
        .only("id", "nome", "prazo")
    )
    for roadmap in roadmaps:
        itens.append(
            {
                "titulo": roadmap.nome,
                "tipo": "Roadmap",
                "prazo": roadmap.prazo,
                "dias": (roadmap.prazo - hoje).days,
                "url": reverse("roadmap:detalhe", args=[roadmap.id]),
                "icone": "bi-signpost-split",
            }
        )
    projetos = (
        Projeto.objects.filter(
            usuario=usuario,
            arquivado_em__isnull=True,
            prazo__isnull=False,
        )
        .exclude(status__in=STATUS_FINAIS_PROJETO)
        .only("id", "titulo", "prazo")
    )
    for projeto in projetos:
        itens.append(
            {
                "titulo": projeto.titulo,
                "tipo": "Projeto",
                "prazo": projeto.prazo,
                "dias": (projeto.prazo - hoje).days,
                "url": reverse("projetos:detalhe", args=[projeto.id]),
                "icone": "bi-kanban",
            }
        )
    competencias = competencias_do_usuario(usuario).filter(
        arquivado_em__isnull=True,
        prazo__isnull=False,
    )
    for competencia in competencias:
        itens.append(
            {
                "titulo": competencia.nome,
                "tipo": "Competência",
                "prazo": competencia.prazo,
                "dias": (competencia.prazo - hoje).days,
                "url": reverse("competencias:detalhe", args=[competencia.id]),
                "icone": "bi-diagram-3",
            }
        )
    acoes_revisao = AcaoRevisao.objects.filter(
        usuario=usuario,
        prazo__isnull=False,
    ).exclude(status__in=(AcaoRevisao.Status.CONCLUIDA, AcaoRevisao.Status.CANCELADA))
    for acao in acoes_revisao.select_related("revisao"):
        itens.append(
            {
                "titulo": acao.descricao,
                "tipo": "Ação de revisão",
                "prazo": acao.prazo,
                "dias": (acao.prazo - hoje).days,
                "url": reverse("revisoes:detalhe", args=[acao.revisao_id]),
                "icone": "bi-arrow-repeat",
            }
        )
    certificacoes = Certificacao.objects.filter(
        usuario=usuario,
        arquivado_em__isnull=True,
        data_prova__isnull=False,
    ).exclude(
        status__in=(
            Certificacao.Status.APROVADA,
            Certificacao.Status.REPROVADA,
            Certificacao.Status.CANCELADA,
            Certificacao.Status.EXPIRADA,
        )
    )
    for certificacao in certificacoes:
        itens.append(
            {
                "titulo": certificacao.nome,
                "tipo": "Prova de certificação",
                "prazo": certificacao.data_prova,
                "dias": (certificacao.data_prova - hoje).days,
                "url": reverse("certificacoes:detalhe", args=[certificacao.id]),
                "icone": "bi-award",
            }
        )
    return sorted(itens, key=lambda item: item["prazo"])[:limite]


def atividades_recentes(usuario, limite=5) -> list[dict]:
    itens = []
    fontes = (
        (
            Objetivo.objects.filter(usuario=usuario, arquivado_em__isnull=True)[:limite],
            "titulo",
            "Objetivo",
            "bi-bullseye",
            "objetivos:detalhe",
        ),
        (
            Roadmap.objects.filter(usuario=usuario, arquivado_em__isnull=True)[:limite],
            "nome",
            "Roadmap",
            "bi-signpost-split",
            "roadmap:detalhe",
        ),
        (
            Aula.objects.filter(usuario=usuario)[:limite],
            "titulo",
            "Aula",
            "bi-journal-text",
            "estudos:aula_detalhe",
        ),
        (
            Anotacao.objects.filter(usuario=usuario)[:limite],
            "titulo",
            "Anotação",
            "bi-pencil-square",
            "anotacoes:editar",
        ),
        (
            Projeto.objects.filter(usuario=usuario, arquivado_em__isnull=True)[:limite],
            "titulo",
            "Projeto",
            "bi-kanban",
            "projetos:detalhe",
        ),
        (
            Competencia.objects.filter(usuario=usuario, arquivado_em__isnull=True)[:limite],
            "nome",
            "Competência",
            "bi-diagram-3",
            "competencias:detalhe",
        ),
        (
            RevisaoPeriodica.objects.filter(usuario=usuario)[:limite],
            "titulo",
            "Revisão",
            "bi-arrow-repeat",
            "revisoes:detalhe",
        ),
        (
            Certificacao.objects.filter(usuario=usuario, arquivado_em__isnull=True)[:limite],
            "nome",
            "Certificação",
            "bi-award",
            "certificacoes:detalhe",
        ),
    )
    for objetos, campo_titulo, tipo, icone, rota in fontes:
        for objeto in objetos:
            itens.append(
                {
                    "titulo": getattr(objeto, campo_titulo),
                    "tipo": tipo,
                    "data": objeto.updated_at,
                    "url": reverse(rota, args=[objeto.id]),
                    "icone": icone,
                }
            )
    return sorted(itens, key=lambda item: item["data"], reverse=True)[:limite]


def evidencias_recentes(usuario, limite=5) -> list[dict]:
    itens = []
    evidencias = Evidencia.objects.filter(usuario=usuario).select_related("projeto")[
        :limite
    ]
    for evidencia in evidencias:
        itens.append(
            {
                "titulo": evidencia.titulo,
                "tipo": evidencia.get_tipo_display(),
                "data": evidencia.data,
                "url": reverse("projetos:detalhe", args=[evidencia.projeto_id]),
                "icone": "bi-image" if evidencia.imagem else "bi-patch-check",
            }
        )
    certificacoes = Certificacao.objects.filter(
        usuario=usuario,
        arquivado_em__isnull=True,
    )[:limite]
    for certificacao in certificacoes:
        itens.append(
            {
                "titulo": certificacao.nome,
                "tipo": "Certificação",
                "data": certificacao.data_prova or certificacao.created_at.date(),
                "url": reverse("certificacoes:detalhe", args=[certificacao.id]),
                "icone": "bi-award",
            }
        )
    return sorted(itens, key=lambda item: item["data"], reverse=True)[:limite]
