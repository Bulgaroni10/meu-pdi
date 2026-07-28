from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from .models import HistoricoObjetivo, Objetivo, Tag


def _texto(valor) -> str:
    if valor is None:
        return ""
    return str(valor)


def _definir_tags(objetivo: Objetivo, tags_texto: str) -> None:
    tags = []
    nomes_vistos = set()
    for nome_bruto in tags_texto.split(","):
        nome = " ".join(nome_bruto.strip().split())
        slug = slugify(nome)
        if not nome or not slug or slug in nomes_vistos:
            continue
        nomes_vistos.add(slug)
        tag, _ = Tag.objects.get_or_create(
            usuario=objetivo.usuario,
            slug=slug,
            defaults={"nome": nome},
        )
        tags.append(tag)
    objetivo.tags.set(tags)


@transaction.atomic
def criar_objetivo(form, usuario) -> Objetivo:
    objetivo = form.save(commit=False)
    objetivo.usuario = usuario
    objetivo.full_clean()
    objetivo.save()
    _definir_tags(objetivo, form.cleaned_data.get("tags_texto", ""))
    HistoricoObjetivo.objects.create(
        objetivo=objetivo,
        usuario=usuario,
        tipo=HistoricoObjetivo.Tipo.CRIACAO,
        descricao="Objetivo criado.",
    )
    return objetivo


@transaction.atomic
def atualizar_objetivo(form, usuario) -> Objetivo:
    anterior = Objetivo.objects.get(pk=form.instance.pk, usuario=usuario)
    objetivo = form.save(commit=False)
    objetivo.usuario = usuario
    objetivo.full_clean()
    objetivo.save()
    _definir_tags(objetivo, form.cleaned_data.get("tags_texto", ""))

    campos = [
        campo for campo in form.changed_data if campo != "tags_texto"
    ]
    for campo in campos:
        HistoricoObjetivo.objects.create(
            objetivo=objetivo,
            usuario=usuario,
            tipo=HistoricoObjetivo.Tipo.ALTERACAO,
            campo=campo,
            valor_anterior=_texto(getattr(anterior, campo)),
            valor_novo=_texto(getattr(objetivo, campo)),
            descricao=f"{form.fields[campo].label} atualizado.",
        )
    if "tags_texto" in form.changed_data:
        HistoricoObjetivo.objects.create(
            objetivo=objetivo,
            usuario=usuario,
            tipo=HistoricoObjetivo.Tipo.ALTERACAO,
            campo="tags",
            descricao="Tags atualizadas.",
        )
    return objetivo


@transaction.atomic
def arquivar_objetivo(objetivo: Objetivo, usuario) -> Objetivo:
    if objetivo.arquivado_em is None:
        objetivo.arquivado_em = timezone.now()
        objetivo.save(update_fields=("arquivado_em", "updated_at"))
        HistoricoObjetivo.objects.create(
            objetivo=objetivo,
            usuario=usuario,
            tipo=HistoricoObjetivo.Tipo.ARQUIVAMENTO,
            descricao="Objetivo arquivado.",
        )
    return objetivo


@transaction.atomic
def restaurar_objetivo(objetivo: Objetivo, usuario) -> Objetivo:
    if objetivo.arquivado_em is not None:
        objetivo.arquivado_em = None
        objetivo.save(update_fields=("arquivado_em", "updated_at"))
        HistoricoObjetivo.objects.create(
            objetivo=objetivo,
            usuario=usuario,
            tipo=HistoricoObjetivo.Tipo.RESTAURACAO,
            descricao="Objetivo restaurado.",
        )
    return objetivo
