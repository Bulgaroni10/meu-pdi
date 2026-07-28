import mimetypes
from pathlib import Path

from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.http import FileResponse
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from .forms import EvidenciaForm, MarcoForm, ProjetoForm, TarefaForm, TecnologiaForm
from .models import (
    Evidencia,
    MarcoProjeto,
    Projeto,
    ProjetoTecnologia,
    TarefaProjeto,
    Tecnologia,
)
from .selectors import projetos_do_usuario
from .services import recalcular_progresso


def lista(request):
    projetos = projetos_do_usuario(request.user).filter(arquivado_em__isnull=True)
    termo = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    if termo:
        projetos = projetos.filter(
            Q(titulo__icontains=termo)
            | Q(problema__icontains=termo)
            | Q(solucao__icontains=termo)
            | Q(tecnologias_vinculadas__tecnologia__nome__icontains=termo)
        ).distinct()
    if status:
        projetos = projetos.filter(status=status)
    return render(
        request,
        "projetos/lista.html",
        {
            "projetos": projetos,
            "status_choices": Projeto.Status.choices,
            "filtros": {"q": termo, "status": status},
        },
    )


def _form_projeto(request, instance=None):
    form = ProjetoForm(request.POST or None, instance=instance, usuario=request.user)
    if request.method == "POST" and form.is_valid():
        projeto = form.save(commit=False)
        projeto.usuario = request.user
        projeto.full_clean()
        projeto.save()
        messages.success(request, "Projeto salvo com sucesso.")
        return redirect("projetos:detalhe", projeto_id=projeto.id)
    return render(
        request,
        "projetos/form.html",
        {
            "form": form,
            "projeto": instance,
            "titulo": "Editar projeto" if instance else "Novo projeto",
        },
    )


def criar(request):
    return _form_projeto(request)


def editar(request, projeto_id):
    projeto = get_object_or_404(Projeto, id=projeto_id, usuario=request.user)
    return _form_projeto(request, projeto)


def detalhe(request, projeto_id):
    projeto = get_object_or_404(
        projetos_do_usuario(request.user).prefetch_related(
            "marcos", "tarefas", "evidencias", "evidencias__material"
        ),
        id=projeto_id,
    )
    return render(request, "projetos/detalhe.html", {"projeto": projeto})


def _projeto_ativo(request, projeto_id):
    return get_object_or_404(
        Projeto,
        id=projeto_id,
        usuario=request.user,
        arquivado_em__isnull=True,
    )


def _form_filho(request, projeto, form, titulo, tipo):
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.usuario = request.user
        item.projeto = projeto
        maior_ordem = (
            item.__class__.objects.filter(projeto=projeto).aggregate(maior=Max("ordem"))[
                "maior"
            ]
            or 0
        )
        item.ordem = maior_ordem + 1
        item.full_clean()
        item.save()
        recalcular_progresso(projeto)
        messages.success(request, f"{tipo} adicionado com sucesso.")
        return redirect("projetos:detalhe", projeto_id=projeto.id)
    return render(
        request,
        "projetos/subitem_form.html",
        {"projeto": projeto, "form": form, "titulo": titulo},
    )


def marco_criar(request, projeto_id):
    projeto = _projeto_ativo(request, projeto_id)
    return _form_filho(
        request,
        projeto,
        MarcoForm(request.POST or None),
        "Novo marco",
        "Marco",
    )


def tarefa_criar(request, projeto_id):
    projeto = _projeto_ativo(request, projeto_id)
    return _form_filho(
        request,
        projeto,
        TarefaForm(request.POST or None),
        "Nova tarefa",
        "Tarefa",
    )


def tecnologia_adicionar(request, projeto_id):
    projeto = _projeto_ativo(request, projeto_id)
    form = TecnologiaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        nome = form.cleaned_data["nome"].strip()
        tecnologia = Tecnologia.objects.filter(
            usuario=request.user, nome__iexact=nome
        ).first()
        if tecnologia is None:
            tecnologia = Tecnologia.objects.create(
                usuario=request.user,
                nome=nome,
                categoria=form.cleaned_data["categoria"],
            )
        ProjetoTecnologia.objects.get_or_create(
            usuario=request.user,
            projeto=projeto,
            tecnologia=tecnologia,
        )
        messages.success(request, "Tecnologia vinculada ao projeto.")
        return redirect("projetos:detalhe", projeto_id=projeto.id)
    return render(
        request,
        "projetos/subitem_form.html",
        {"projeto": projeto, "form": form, "titulo": "Adicionar tecnologia"},
    )


def evidencia_criar(request, projeto_id):
    projeto = _projeto_ativo(request, projeto_id)
    form = EvidenciaForm(
        request.POST or None,
        request.FILES or None,
        usuario=request.user,
    )
    if request.method == "POST" and form.is_valid():
        evidencia = form.save(commit=False)
        evidencia.usuario = request.user
        evidencia.projeto = projeto
        evidencia.full_clean()
        evidencia.save()
        messages.success(request, "Evidência adicionada ao projeto.")
        return redirect("projetos:detalhe", projeto_id=projeto.id)
    return render(
        request,
        "projetos/subitem_form.html",
        {"projeto": projeto, "form": form, "titulo": "Nova evidência"},
    )


def evidencia_editar(request, projeto_id, evidencia_id):
    projeto = _projeto_ativo(request, projeto_id)
    evidencia = get_object_or_404(
        Evidencia, id=evidencia_id, projeto=projeto, usuario=request.user
    )
    imagem_anterior = evidencia.imagem.name
    form = EvidenciaForm(
        request.POST or None,
        request.FILES or None,
        instance=evidencia,
        usuario=request.user,
    )
    if request.method == "POST" and form.is_valid():
        evidencia = form.save(commit=False)
        evidencia.usuario = request.user
        evidencia.projeto = projeto
        evidencia.full_clean()
        evidencia.save()
        if (
            imagem_anterior
            and evidencia.imagem.name != imagem_anterior
            and evidencia.imagem.storage.exists(imagem_anterior)
        ):
            evidencia.imagem.storage.delete(imagem_anterior)
        messages.success(request, "Evidência atualizada.")
        return redirect("projetos:detalhe", projeto_id=projeto.id)
    return render(
        request,
        "projetos/subitem_form.html",
        {"projeto": projeto, "form": form, "titulo": "Editar evidência"},
    )


def evidencia_confirmar_exclusao(request, projeto_id, evidencia_id):
    projeto = _projeto_ativo(request, projeto_id)
    evidencia = get_object_or_404(
        Evidencia, id=evidencia_id, projeto=projeto, usuario=request.user
    )
    return render(
        request,
        "projetos/evidencia_confirmar_exclusao.html",
        {"projeto": projeto, "evidencia": evidencia},
    )


@require_POST
def evidencia_excluir(request, projeto_id, evidencia_id):
    projeto = _projeto_ativo(request, projeto_id)
    evidencia = get_object_or_404(
        Evidencia, id=evidencia_id, projeto=projeto, usuario=request.user
    )
    imagem = evidencia.imagem
    try:
        evidencia.delete()
    except ProtectedError:
        messages.error(
            request,
            "Esta evidência é usada em uma competência e não pode ser excluída.",
        )
    else:
        if imagem and imagem.storage.exists(imagem.name):
            imagem.storage.delete(imagem.name)
        messages.success(request, "Evidência excluída.")
    return redirect("projetos:detalhe", projeto_id=projeto.id)


@xframe_options_sameorigin
def evidencia_imagem(request, projeto_id, evidencia_id):
    evidencia = get_object_or_404(
        Evidencia,
        id=evidencia_id,
        projeto_id=projeto_id,
        usuario=request.user,
        imagem__isnull=False,
    )
    if not evidencia.imagem.name:
        return redirect("projetos:detalhe", projeto_id=projeto_id)
    content_type, _ = mimetypes.guess_type(Path(evidencia.imagem.name).name)
    resposta = FileResponse(
        evidencia.imagem.open("rb"),
        content_type=content_type or "application/octet-stream",
    )
    resposta["Content-Disposition"] = "inline"
    resposta["Cache-Control"] = "private, no-store"
    resposta["X-Content-Type-Options"] = "nosniff"
    return resposta


@require_POST
def tarefa_alternar(request, projeto_id, tarefa_id):
    projeto = _projeto_ativo(request, projeto_id)
    tarefa = get_object_or_404(
        TarefaProjeto, id=tarefa_id, projeto=projeto, usuario=request.user
    )
    tarefa.status = (
        TarefaProjeto.Status.PENDENTE
        if tarefa.status == TarefaProjeto.Status.CONCLUIDA
        else TarefaProjeto.Status.CONCLUIDA
    )
    tarefa.save(update_fields=("status", "updated_at"))
    recalcular_progresso(projeto)
    return redirect("projetos:detalhe", projeto_id=projeto.id)


@require_POST
def marco_alternar(request, projeto_id, marco_id):
    projeto = _projeto_ativo(request, projeto_id)
    marco = get_object_or_404(
        MarcoProjeto, id=marco_id, projeto=projeto, usuario=request.user
    )
    marco.status = (
        MarcoProjeto.Status.PENDENTE
        if marco.status == MarcoProjeto.Status.CONCLUIDO
        else MarcoProjeto.Status.CONCLUIDO
    )
    marco.save(update_fields=("status", "updated_at"))
    recalcular_progresso(projeto)
    return redirect("projetos:detalhe", projeto_id=projeto.id)


@require_POST
def arquivar(request, projeto_id):
    projeto = get_object_or_404(Projeto, id=projeto_id, usuario=request.user)
    projeto.arquivado_em = timezone.now()
    projeto.save(update_fields=("arquivado_em", "updated_at"))
    messages.success(request, "Projeto arquivado.")
    return redirect("projetos:lista")
