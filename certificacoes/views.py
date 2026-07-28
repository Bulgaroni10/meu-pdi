from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CertificacaoForm
from .models import Certificacao


def certificacoes_do_usuario(usuario):
    return Certificacao.objects.filter(usuario=usuario).select_related(
        "objetivo", "trilha", "certificado"
    )


def lista(request):
    certificacoes = certificacoes_do_usuario(request.user).filter(
        arquivado_em__isnull=True
    )
    termo = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    if termo:
        certificacoes = certificacoes.filter(
            Q(nome__icontains=termo)
            | Q(codigo__icontains=termo)
            | Q(instituicao__icontains=termo)
        )
    if status:
        certificacoes = certificacoes.filter(status=status)
    return render(
        request,
        "certificacoes/lista.html",
        {
            "certificacoes": certificacoes,
            "status_choices": Certificacao.Status.choices,
            "filtros": {"q": termo, "status": status},
        },
    )


def _form(request, instance=None):
    form = CertificacaoForm(
        request.POST or None,
        instance=instance,
        usuario=request.user,
    )
    if request.method == "POST" and form.is_valid():
        certificacao = form.save(commit=False)
        certificacao.usuario = request.user
        certificacao.full_clean()
        certificacao.save()
        messages.success(request, "Certificação salva com sucesso.")
        return redirect("certificacoes:detalhe", certificacao_id=certificacao.id)
    return render(
        request,
        "certificacoes/form.html",
        {
            "form": form,
            "certificacao": instance,
            "titulo": "Editar certificação" if instance else "Nova certificação",
        },
    )


def criar(request):
    return _form(request)


def editar(request, certificacao_id):
    certificacao = get_object_or_404(
        Certificacao, id=certificacao_id, usuario=request.user
    )
    return _form(request, certificacao)


def detalhe(request, certificacao_id):
    certificacao = get_object_or_404(
        certificacoes_do_usuario(request.user), id=certificacao_id
    )
    return render(
        request,
        "certificacoes/detalhe.html",
        {"certificacao": certificacao},
    )


@require_POST
def arquivar(request, certificacao_id):
    certificacao = get_object_or_404(
        Certificacao, id=certificacao_id, usuario=request.user
    )
    certificacao.arquivado_em = timezone.now()
    certificacao.save(update_fields=("arquivado_em", "updated_at"))
    messages.success(request, "Certificação arquivada.")
    return redirect("certificacoes:lista")
