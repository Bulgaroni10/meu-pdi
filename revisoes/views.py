from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AcaoRevisaoForm, RevisaoForm
from .models import AcaoRevisao, RevisaoPeriodica


def revisoes_do_usuario(usuario):
    return RevisaoPeriodica.objects.filter(usuario=usuario).prefetch_related(
        "acoes", "acoes__objetivo", "acoes__projeto", "acoes__competencia"
    )


def lista(request):
    revisoes = revisoes_do_usuario(request.user)
    tipo = request.GET.get("tipo", "").strip()
    if tipo:
        revisoes = revisoes.filter(tipo=tipo)
    return render(
        request,
        "revisoes/lista.html",
        {
            "revisoes": revisoes,
            "tipos": RevisaoPeriodica.Tipo.choices,
            "tipo_atual": tipo,
        },
    )


def _form(request, instance=None):
    form = RevisaoForm(request.POST or None, instance=instance, usuario=request.user)
    if request.method == "POST" and form.is_valid():
        revisao = form.save(commit=False)
        revisao.usuario = request.user
        revisao.full_clean()
        revisao.save()
        messages.success(request, "Revisão salva com sucesso.")
        return redirect("revisoes:detalhe", revisao_id=revisao.id)
    return render(
        request,
        "revisoes/form.html",
        {
            "form": form,
            "revisao": instance,
            "titulo": "Editar revisão" if instance else "Nova revisão",
        },
    )


def criar(request):
    return _form(request)


def editar(request, revisao_id):
    revisao = get_object_or_404(
        RevisaoPeriodica, id=revisao_id, usuario=request.user
    )
    return _form(request, revisao)


def detalhe(request, revisao_id):
    revisao = get_object_or_404(
        revisoes_do_usuario(request.user), id=revisao_id
    )
    return render(request, "revisoes/detalhe.html", {"revisao": revisao})


def acao_criar(request, revisao_id):
    revisao = get_object_or_404(
        RevisaoPeriodica, id=revisao_id, usuario=request.user
    )
    form = AcaoRevisaoForm(
        request.POST or None,
        usuario=request.user,
        revisao=revisao,
    )
    if request.method == "POST" and form.is_valid():
        acao = form.save(commit=False)
        acao.usuario = request.user
        acao.revisao = revisao
        acao.full_clean()
        acao.save()
        messages.success(request, "Próxima ação adicionada.")
        return redirect("revisoes:detalhe", revisao_id=revisao.id)
    return render(
        request,
        "revisoes/acao_form.html",
        {"revisao": revisao, "form": form},
    )


@require_POST
def acao_alternar(request, revisao_id, acao_id):
    revisao = get_object_or_404(
        RevisaoPeriodica, id=revisao_id, usuario=request.user
    )
    acao = get_object_or_404(
        AcaoRevisao, id=acao_id, revisao=revisao, usuario=request.user
    )
    acao.status = (
        AcaoRevisao.Status.PENDENTE
        if acao.status == AcaoRevisao.Status.CONCLUIDA
        else AcaoRevisao.Status.CONCLUIDA
    )
    acao.save(update_fields=("status", "updated_at"))
    return redirect("revisoes:detalhe", revisao_id=revisao.id)


@require_POST
def concluir(request, revisao_id):
    revisao = get_object_or_404(
        RevisaoPeriodica, id=revisao_id, usuario=request.user
    )
    revisao.status = RevisaoPeriodica.Status.CONCLUIDA
    revisao.save(update_fields=("status", "concluida_em", "updated_at"))
    messages.success(request, "Ciclo de revisão concluído.")
    return redirect("revisoes:detalhe", revisao_id=revisao.id)
