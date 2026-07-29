from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import FiltroObjetivoForm, ObjetivoForm
from .models import Objetivo
from .selectors import objetivos_do_usuario, objetivos_filtrados, resumo_objetivos
from .services import (
    arquivar_objetivo,
    atualizar_objetivo,
    criar_objetivo,
    restaurar_objetivo,
)


def lista(request):
    filtros_form = FiltroObjetivoForm(request.GET)
    filtros = filtros_form.cleaned_data if filtros_form.is_valid() else {}
    paginator = Paginator(objetivos_filtrados(request.user, filtros), 9)
    pagina = paginator.get_page(request.GET.get("pagina"))
    query_params = request.GET.copy()
    query_params.pop("pagina", None)
    context = {
        "filtros_form": filtros_form,
        "pagina": pagina,
        "resumo": resumo_objetivos(request.user),
        "query_params": query_params.urlencode(),
        "status_atual": request.GET.get("status", ""),
    }
    if request.headers.get("HX-Request") == "true":
        return render(request, "objetivos/_lista_resultados.html", context)
    return render(request, "objetivos/lista.html", context)


def criar(request):
    if request.method == "POST":
        form = ObjetivoForm(request.POST)
        if form.is_valid():
            objetivo = criar_objetivo(form, request.user)
            messages.success(request, "Objetivo criado com sucesso.")
            return redirect("objetivos:detalhe", objetivo.id)
    else:
        form = ObjetivoForm()
    return render(
        request,
        "objetivos/form.html",
        {"form": form, "titulo": "Novo objetivo", "acao": "Criar objetivo"},
    )


def detalhe(request, objetivo_id):
    objetivo = get_object_or_404(
        objetivos_do_usuario(request.user),
        id=objetivo_id,
    )
    return render(request, "objetivos/detalhe.html", {"objetivo": objetivo})


def editar(request, objetivo_id):
    objetivo = get_object_or_404(
        objetivos_do_usuario(request.user),
        id=objetivo_id,
    )
    if request.method == "POST":
        form = ObjetivoForm(request.POST, instance=objetivo)
        if form.is_valid():
            objetivo = atualizar_objetivo(form, request.user)
            messages.success(request, "Objetivo atualizado com sucesso.")
            return redirect("objetivos:detalhe", objetivo.id)
    else:
        form = ObjetivoForm(instance=objetivo)
    return render(
        request,
        "objetivos/form.html",
        {
            "form": form,
            "objetivo": objetivo,
            "titulo": "Editar objetivo",
            "acao": "Salvar alterações",
        },
    )


def arquivar(request, objetivo_id):
    objetivo = get_object_or_404(
        objetivos_do_usuario(request.user),
        id=objetivo_id,
    )
    if request.method == "POST":
        arquivar_objetivo(objetivo, request.user)
        messages.success(request, "Objetivo arquivado.")
        return redirect("objetivos:lista")
    return render(request, "objetivos/confirmar_arquivamento.html", {"objetivo": objetivo})


@require_POST
def restaurar(request, objetivo_id):
    objetivo = get_object_or_404(
        objetivos_do_usuario(request.user),
        id=objetivo_id,
    )
    restaurar_objetivo(objetivo, request.user)
    messages.success(request, "Objetivo restaurado.")
    return redirect("objetivos:detalhe", objetivo.id)
