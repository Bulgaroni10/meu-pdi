import hashlib
import re
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import (
    EntregaRoadmap,
    EtapaRoadmap,
    FaseRoadmap,
    FonteRoadmap,
    Roadmap,
)
from .pdf_parser import DocumentoExtraido, extrair_pdf


def _resumo(texto: str, limite: int = 650) -> str:
    texto = re.sub(r"\s+", " ", texto).strip()
    if len(texto) <= limite:
        return texto
    trecho = texto[:limite].rsplit(" ", 1)[0]
    return f"{trecho}..."


def _topicos(texto: str, titulo_fase: str) -> list[tuple[str, str]]:
    candidatos = []
    for parte in re.split(r"(?:\n|(?<=[.!?])\s+)", texto):
        parte = re.sub(r"^[•●▪◦*\-\d.)\s]+", "", parte).strip()
        if 18 <= len(parte) <= 260:
            chave = re.sub(r"\W+", "", parte.casefold())
            if chave and all(chave != item[0] for item in candidatos):
                candidatos.append((chave, parte))
        if len(candidatos) == 3:
            break
    if not candidatos:
        return [(f"estudar{titulo_fase}", f"Estudar e resumir {titulo_fase}.")]
    return [
        (_resumo(parte, 110), _resumo(parte, 260))
        for _, parte in candidatos
    ]


@transaction.atomic
def recalcular_progresso_fase(fase: FaseRoadmap) -> int:
    total = fase.etapas.count()
    concluidas = fase.etapas.filter(concluida=True).count()
    progresso = round((concluidas / total) * 100) if total else 0
    if total and concluidas == total:
        status = FaseRoadmap.Status.CONCLUIDA
        data_real = fase.data_real_conclusao or timezone.localdate()
    elif concluidas:
        status = FaseRoadmap.Status.EM_ANDAMENTO
        data_real = None
    else:
        status = FaseRoadmap.Status.NAO_INICIADA
        data_real = None
    FaseRoadmap.objects.filter(pk=fase.pk).update(
        progresso=progresso,
        status=status,
        data_real_conclusao=data_real,
        updated_at=timezone.now(),
    )

    roadmap = fase.roadmap
    fases = roadmap.fases.all()
    if fases.exists() and not fases.exclude(
        status=FaseRoadmap.Status.CONCLUIDA
    ).exists():
        status_roadmap = Roadmap.Status.CONCLUIDO
    elif fases.filter(progresso__gt=0).exists():
        status_roadmap = Roadmap.Status.EM_ANDAMENTO
    else:
        status_roadmap = Roadmap.Status.PLANEJADO
    Roadmap.objects.filter(pk=roadmap.pk).update(
        status=status_roadmap,
        updated_at=timezone.now(),
    )
    return progresso


@transaction.atomic
def criar_roadmap_do_pdf(*, usuario, arquivo, nome: str, objetivo=None) -> Roadmap:
    documento: DocumentoExtraido = extrair_pdf(arquivo)
    arquivo.seek(0)
    digest = hashlib.sha256(arquivo.read()).hexdigest()
    arquivo.seek(0)

    fonte = FonteRoadmap(
        usuario=usuario,
        nome_original=arquivo.name[:255],
        mime_type="application/pdf",
        tamanho=arquivo.size,
        sha256=digest,
        quantidade_paginas=documento.paginas,
        titulo_extraido=documento.titulo,
    )
    fonte.arquivo.save(arquivo.name, arquivo, save=False)

    inicio = timezone.localdate()
    quantidade = len(documento.secoes)
    roadmap = None
    try:
        fonte.full_clean()
        fonte.save()
        roadmap = Roadmap(
            usuario=usuario,
            nome=(nome.strip() or documento.titulo)[:180],
            descricao=(
                f"Roadmap criado localmente a partir de {fonte.nome_original}, "
                f"com {documento.paginas} página(s) e {quantidade} fase(s) identificadas."
            ),
            objetivo=objetivo,
            fonte_pdf=fonte,
            data_inicio=inicio,
            prazo=inicio + timedelta(days=max(30, quantidade * 30)),
            status=Roadmap.Status.RASCUNHO,
            prioridade=Roadmap.Prioridade.MEDIA,
            gerado_de_pdf=True,
            observacoes=(
                "Conteúdo gerado automaticamente a partir da estrutura textual "
                "do PDF. Revise títulos, ordem e entregas antes de iniciar."
            ),
        )
        roadmap.full_clean()
        roadmap.save()

        for ordem, secao in enumerate(documento.secoes, start=1):
            inicio_fase = inicio + timedelta(days=(ordem - 1) * 30)
            fase = FaseRoadmap.objects.create(
                usuario=usuario,
                roadmap=roadmap,
                titulo=secao.titulo[:180],
                descricao=_resumo(secao.conteudo),
                ordem=ordem,
                data_prevista_inicio=inicio_fase,
                data_prevista_conclusao=inicio_fase + timedelta(days=29),
                criterios_conclusao=(
                    "Concluir as etapas, registrar um resumo e produzir a "
                    "evidência prática prevista."
                ),
                dependencias=(
                    f"Conclusão da fase {ordem - 1}."
                    if ordem > 1
                    else "Nenhuma dependência."
                ),
                proxima_acao=f"Ler e organizar o conteúdo de {secao.titulo[:150]}.",
            )
            for ordem_etapa, (titulo, descricao) in enumerate(
                _topicos(secao.conteudo, secao.titulo),
                start=1,
            ):
                EtapaRoadmap.objects.create(
                    usuario=usuario,
                    fase=fase,
                    titulo=titulo[:180],
                    descricao=descricao,
                    ordem=ordem_etapa,
                )
            EntregaRoadmap.objects.create(
                usuario=usuario,
                fase=fase,
                titulo=f"Evidência prática - {secao.titulo}"[:180],
                descricao=(
                    "Produzir uma evidência aplicável do aprendizado desta fase: "
                    "resumo, laboratório, exercício, documentação ou projeto."
                ),
                criterio_aceite=(
                    "A evidência deve explicar o que foi aprendido, como foi "
                    "aplicado e qual resultado foi obtido."
                ),
            )
    except Exception:
        fonte.arquivo.delete(save=False)
        raise

    return roadmap
