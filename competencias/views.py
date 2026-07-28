from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AvaliacaoForm, CompetenciaForm
from .models import AvaliacaoCompetencia, Competencia, EvidenciaCompetencia
from .selectors import competencias_do_usuario


def lista(request):
    competencias = competencias_do_usuario(request.user).filter(
        arquivado_em__isnull=True
    )
    categoria = request.GET.get("categoria", "").strip()
    if categoria:
        competencias = competencias.filter(categoria=categoria)
    return render(
        request,
        "competencias/lista.html",
        {
            "competencias": competencias,
            "categorias": Competencia.Categoria.choices,
            "categoria_atual": categoria,
        },
    )


def _form(request, instance=None):
    form = CompetenciaForm(
        request.POST or None,
        instance=instance,
        usuario=request.user,
    )
    if request.method == "POST" and form.is_valid():
        competencia = form.save(commit=False)
        competencia.usuario = request.user
        competencia.full_clean()
        competencia.save()
        messages.success(request, "Competência salva com sucesso.")
        return redirect("competencias:detalhe", competencia_id=competencia.id)
    return render(
        request,
        "competencias/form.html",
        {
            "form": form,
            "competencia": instance,
            "titulo": "Editar competência" if instance else "Nova competência",
        },
    )


def criar(request):
    return _form(request)


def editar(request, competencia_id):
    competencia = get_object_or_404(
        Competencia, id=competencia_id, usuario=request.user
    )
    return _form(request, competencia)


def detalhe(request, competencia_id):
    competencia = get_object_or_404(
        competencias_do_usuario(request.user).prefetch_related(
            "avaliacoes", "avaliacoes__evidencias", "avaliacoes__evidencias__projeto"
        ),
        id=competencia_id,
    )
    return render(
        request,
        "competencias/detalhe.html",
        {"competencia": competencia},
    )


@transaction.atomic
def avaliar(request, competencia_id):
    competencia = get_object_or_404(
        Competencia,
        id=competencia_id,
        usuario=request.user,
        arquivado_em__isnull=True,
    )
    form = AvaliacaoForm(request.POST or None, usuario=request.user)
    if request.method == "POST" and form.is_valid():
        avaliacao = form.save(commit=False)
        avaliacao.usuario = request.user
        avaliacao.competencia = competencia
        avaliacao.full_clean()
        avaliacao.save()
        for evidencia in form.cleaned_data["evidencias"]:
            EvidenciaCompetencia.objects.create(
                usuario=request.user,
                avaliacao=avaliacao,
                evidencia=evidencia,
            )
        messages.success(request, "Avaliação registrada com evidências.")
        return redirect("competencias:detalhe", competencia_id=competencia.id)
    return render(
        request,
        "competencias/avaliar.html",
        {"competencia": competencia, "form": form},
    )


@require_POST
def arquivar(request, competencia_id):
    competencia = get_object_or_404(
        Competencia, id=competencia_id, usuario=request.user
    )
    competencia.arquivado_em = timezone.now()
    competencia.save(update_fields=("arquivado_em", "updated_at"))
    messages.success(request, "Competência arquivada.")
    return redirect("competencias:lista")
