import bleach
from django.db import transaction
from django.utils.html import strip_tags

from .models import Anotacao, VersaoAnotacao


TAGS_PERMITIDAS = {
    "p", "br", "h1", "h2", "h3", "h4", "strong", "em", "u", "s",
    "ul", "ol", "li", "a", "blockquote", "pre", "code", "mark",
}
ATRIBUTOS_PERMITIDOS = {"a": ["href", "title", "target", "rel"], "li": ["data-list"]}


def sanitizar_html(html):
    return bleach.clean(
        html or "",
        tags=TAGS_PERMITIDAS,
        attributes=ATRIBUTOS_PERMITIDOS,
        protocols={"http", "https", "mailto"},
        strip=True,
    )


def _texto(html):
    return " ".join(strip_tags(html).split())


@transaction.atomic
def criar_anotacao(form, usuario):
    anotacao = form.save(commit=False)
    anotacao.usuario = usuario
    anotacao.conteudo_html = sanitizar_html(anotacao.conteudo_html)
    anotacao.conteudo_texto = _texto(anotacao.conteudo_html)
    anotacao.full_clean()
    anotacao.save()
    VersaoAnotacao.objects.create(
        usuario=usuario, anotacao=anotacao, numero=1, titulo=anotacao.titulo,
        conteudo_html=anotacao.conteudo_html, conteudo_texto=anotacao.conteudo_texto,
    )
    return anotacao


@transaction.atomic
def autosalvar(anotacao, usuario, *, titulo, html, pagina, versao_cliente):
    anotacao = Anotacao.objects.select_for_update().get(pk=anotacao.pk, usuario=usuario)
    if versao_cliente != anotacao.versao_atual:
        raise ValueError("CONFLITO")
    html_limpo = sanitizar_html(html)
    titulo = (titulo or anotacao.titulo).strip()[:180]
    mudou = html_limpo != anotacao.conteudo_html or titulo != anotacao.titulo
    anotacao.titulo = titulo
    anotacao.conteudo_html = html_limpo
    anotacao.conteudo_texto = _texto(html_limpo)
    anotacao.pagina_pdf = pagina or None
    if mudou:
        anotacao.versao_atual += 1
    anotacao.save()
    if mudou:
        VersaoAnotacao.objects.create(
            usuario=usuario, anotacao=anotacao, numero=anotacao.versao_atual,
            titulo=anotacao.titulo, conteudo_html=anotacao.conteudo_html,
            conteudo_texto=anotacao.conteudo_texto,
        )
    return anotacao


@transaction.atomic
def restaurar_versao(anotacao, versao, usuario):
    anotacao.conteudo_html = versao.conteudo_html
    anotacao.conteudo_texto = versao.conteudo_texto
    anotacao.titulo = versao.titulo
    anotacao.versao_atual += 1
    anotacao.save()
    VersaoAnotacao.objects.create(
        usuario=usuario, anotacao=anotacao, numero=anotacao.versao_atual,
        titulo=anotacao.titulo, conteudo_html=anotacao.conteudo_html,
        conteudo_texto=anotacao.conteudo_texto,
    )
    return anotacao
