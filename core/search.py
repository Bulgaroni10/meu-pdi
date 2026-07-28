from django.db.models import Q
from django.urls import reverse

from anotacoes.models import Anotacao
from biblioteca.models import MaterialPDF
from certificacoes.models import Certificacao
from competencias.models import Competencia
from estudos.models import Aula, Curso, Disciplina, Trilha
from objetivos.models import Objetivo
from projetos.models import Projeto
from revisoes.models import RevisaoPeriodica
from roadmap.models import Roadmap


LIMITE_POR_GRUPO = 8


def _itens(queryset, *, titulo, subtitulo, rota, icone, descricao=None):
    resultados = []
    for objeto in queryset[:LIMITE_POR_GRUPO]:
        resultados.append(
            {
                "titulo": getattr(objeto, titulo),
                "subtitulo": subtitulo(objeto),
                "descricao": getattr(objeto, descricao, "") if descricao else "",
                "url": reverse(rota, args=[objeto.id]),
                "icone": icone,
            }
        )
    return resultados


def buscar_tudo(usuario, termo: str) -> list[dict]:
    termo = termo.strip()
    if not termo:
        return []

    grupos = [
        {
            "nome": "Objetivos",
            "itens": _itens(
                Objetivo.objects.filter(
                    Q(titulo__icontains=termo)
                    | Q(descricao__icontains=termo)
                    | Q(proxima_acao__icontains=termo),
                    usuario=usuario,
                    arquivado_em__isnull=True,
                ),
                titulo="titulo",
                subtitulo=lambda item: item.status_efetivo_label,
                descricao="descricao",
                rota="objetivos:detalhe",
                icone="bi-bullseye",
            ),
        },
        {
            "nome": "Roadmaps",
            "itens": _itens(
                Roadmap.objects.filter(
                    Q(nome__icontains=termo) | Q(descricao__icontains=termo),
                    usuario=usuario,
                    arquivado_em__isnull=True,
                ),
                titulo="nome",
                subtitulo=lambda item: item.get_status_display(),
                descricao="descricao",
                rota="roadmap:detalhe",
                icone="bi-signpost-split",
            ),
        },
        {
            "nome": "Trilhas e cursos",
            "itens": [
                *_itens(
                    Trilha.objects.filter(
                        Q(titulo__icontains=termo) | Q(descricao__icontains=termo),
                        usuario=usuario,
                    ),
                    titulo="titulo",
                    subtitulo=lambda item: f"Trilha · {item.get_categoria_display()}",
                    descricao="descricao",
                    rota="estudos:trilha_editar",
                    icone="bi-map",
                ),
                *_itens(
                    Curso.objects.filter(
                        Q(nome__icontains=termo)
                        | Q(instituicao__icontains=termo)
                        | Q(descricao__icontains=termo),
                        usuario=usuario,
                    ),
                    titulo="nome",
                    subtitulo=lambda item: f"Curso · {item.instituicao or item.get_tipo_display()}",
                    descricao="descricao",
                    rota="estudos:curso_detalhe",
                    icone="bi-mortarboard",
                ),
            ][:LIMITE_POR_GRUPO],
        },
        {
            "nome": "Disciplinas e aulas",
            "itens": [
                *_itens(
                    Disciplina.objects.filter(
                        Q(nome__icontains=termo)
                        | Q(ementa__icontains=termo)
                        | Q(descricao__icontains=termo),
                        usuario=usuario,
                    ),
                    titulo="nome",
                    subtitulo=lambda item: f"Disciplina · {item.curso.nome}",
                    descricao="descricao",
                    rota="estudos:disciplina_editar",
                    icone="bi-journal",
                ),
                *_itens(
                    Aula.objects.filter(
                        Q(titulo__icontains=termo)
                        | Q(descricao__icontains=termo)
                        | Q(resumo__icontains=termo)
                        | Q(tags__icontains=termo),
                        usuario=usuario,
                    ),
                    titulo="titulo",
                    subtitulo=lambda item: f"Aula · {item.disciplina.nome}",
                    descricao="descricao",
                    rota="estudos:aula_detalhe",
                    icone="bi-journal-text",
                ),
            ][:LIMITE_POR_GRUPO],
        },
        {
            "nome": "Anotações",
            "itens": _itens(
                Anotacao.objects.filter(
                    Q(titulo__icontains=termo)
                    | Q(conteudo_texto__icontains=termo)
                    | Q(tags__icontains=termo),
                    usuario=usuario,
                ),
                titulo="titulo",
                subtitulo=lambda item: f"{item.get_tipo_display()} · {item.aula.titulo}",
                descricao="conteudo_texto",
                rota="anotacoes:editar",
                icone="bi-pencil-square",
            ),
        },
        {
            "nome": "Biblioteca",
            "itens": _itens(
                MaterialPDF.objects.filter(
                    Q(titulo__icontains=termo)
                    | Q(descricao__icontains=termo)
                    | Q(nome_original__icontains=termo),
                    usuario=usuario,
                ),
                titulo="titulo",
                subtitulo=lambda item: f"PDF · {item.quantidade_paginas} páginas",
                descricao="descricao",
                rota="biblioteca:abrir",
                icone="bi-file-earmark-pdf",
            ),
        },
        {
            "nome": "Projetos",
            "itens": _itens(
                Projeto.objects.filter(
                    Q(titulo__icontains=termo)
                    | Q(problema__icontains=termo)
                    | Q(solucao__icontains=termo)
                    | Q(aprendizados__icontains=termo),
                    usuario=usuario,
                    arquivado_em__isnull=True,
                ),
                titulo="titulo",
                subtitulo=lambda item: item.get_status_display(),
                descricao="solucao",
                rota="projetos:detalhe",
                icone="bi-kanban",
            ),
        },
        {
            "nome": "Competências",
            "itens": _itens(
                Competencia.objects.filter(
                    Q(nome__icontains=termo)
                    | Q(descricao__icontains=termo)
                    | Q(criterios__icontains=termo),
                    usuario=usuario,
                    arquivado_em__isnull=True,
                ),
                titulo="nome",
                subtitulo=lambda item: item.get_categoria_display(),
                descricao="descricao",
                rota="competencias:detalhe",
                icone="bi-diagram-3",
            ),
        },
        {
            "nome": "Revisões",
            "itens": _itens(
                RevisaoPeriodica.objects.filter(
                    Q(titulo__icontains=termo)
                    | Q(conquistas__icontains=termo)
                    | Q(dificuldades__icontains=termo)
                    | Q(aprendizados__icontains=termo)
                    | Q(ajustes__icontains=termo)
                    | Q(conclusao__icontains=termo),
                    usuario=usuario,
                ),
                titulo="titulo",
                subtitulo=lambda item: item.get_tipo_display(),
                descricao="conclusao",
                rota="revisoes:detalhe",
                icone="bi-arrow-repeat",
            ),
        },
        {
            "nome": "Certificações",
            "itens": _itens(
                Certificacao.objects.filter(
                    Q(nome__icontains=termo)
                    | Q(codigo__icontains=termo)
                    | Q(instituicao__icontains=termo)
                    | Q(observacoes__icontains=termo),
                    usuario=usuario,
                    arquivado_em__isnull=True,
                ),
                titulo="nome",
                subtitulo=lambda item: f"{item.instituicao} · {item.codigo}".strip(" ·"),
                descricao="observacoes",
                rota="certificacoes:detalhe",
                icone="bi-award",
            ),
        },
    ]
    return [grupo for grupo in grupos if grupo["itens"]]
