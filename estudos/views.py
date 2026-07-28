from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AulaForm, CursoForm, DisciplinaForm, PeriodoForm, TrilhaForm
from .models import Aula, Curso, Disciplina, Periodo, Trilha
from .selectors import cursos_do_usuario, disciplinas_do_usuario, resumo_estudos


def inicio(request):
    return render(
        request,
        "estudos/inicio.html",
        {
            "resumo": resumo_estudos(request.user),
            "trilhas": Trilha.objects.filter(usuario=request.user)[:4],
            "cursos": cursos_do_usuario(request.user)[:4],
            "aulas": Aula.objects.filter(usuario=request.user).select_related("disciplina")[:6],
        },
    )


def _form(request, form_class, *, titulo, tipo, instance=None, redirect_name="estudos:inicio"):
    form = form_class(
        request.POST or None,
        instance=instance,
        usuario=request.user,
    )
    if request.method == "POST" and form.is_valid():
        objeto = form.save(commit=False)
        objeto.usuario = request.user
        objeto.full_clean()
        objeto.save()
        form.save_m2m()
        messages.success(request, f"{tipo} salvo com sucesso.")
        return redirect(redirect_name)
    return render(
        request,
        "estudos/form.html",
        {"form": form, "titulo": titulo, "tipo": tipo},
    )


def trilhas(request):
    return render(
        request, "estudos/trilhas.html", {"trilhas": Trilha.objects.filter(usuario=request.user)}
    )


def trilha_criar(request):
    return _form(request, TrilhaForm, titulo="Nova trilha", tipo="Trilha", redirect_name="estudos:trilhas")


def trilha_editar(request, item_id):
    item = get_object_or_404(Trilha, id=item_id, usuario=request.user)
    return _form(request, TrilhaForm, titulo="Editar trilha", tipo="Trilha", instance=item, redirect_name="estudos:trilhas")


def cursos(request):
    return render(request, "estudos/cursos.html", {"cursos": cursos_do_usuario(request.user)})


def curso_criar(request):
    return _form(request, CursoForm, titulo="Novo curso", tipo="Curso", redirect_name="estudos:cursos")


def curso_editar(request, item_id):
    item = get_object_or_404(Curso, id=item_id, usuario=request.user)
    return _form(request, CursoForm, titulo="Editar curso", tipo="Curso", instance=item, redirect_name="estudos:cursos")


def curso_detalhe(request, item_id):
    curso = get_object_or_404(cursos_do_usuario(request.user), id=item_id)
    return render(request, "estudos/curso_detalhe.html", {"curso": curso})


def periodo_criar(request):
    return _form(request, PeriodoForm, titulo="Novo período", tipo="Período", redirect_name="estudos:cursos")


def disciplinas(request):
    return render(
        request, "estudos/disciplinas.html", {"disciplinas": disciplinas_do_usuario(request.user)}
    )


def disciplina_criar(request):
    return _form(request, DisciplinaForm, titulo="Nova disciplina", tipo="Disciplina", redirect_name="estudos:disciplinas")


def disciplina_editar(request, item_id):
    item = get_object_or_404(Disciplina, id=item_id, usuario=request.user)
    return _form(request, DisciplinaForm, titulo="Editar disciplina", tipo="Disciplina", instance=item, redirect_name="estudos:disciplinas")


def disciplina_detalhe(request, item_id):
    disciplina = get_object_or_404(
        disciplinas_do_usuario(request.user).prefetch_related("aulas"),
        id=item_id,
    )
    return render(
        request,
        "estudos/disciplina_detalhe.html",
        {"disciplina": disciplina},
    )


def aulas(request):
    queryset = Aula.objects.filter(usuario=request.user).select_related("disciplina", "disciplina__curso")
    return render(request, "estudos/aulas.html", {"aulas": queryset})


def aula_criar(request):
    return _form(request, AulaForm, titulo="Nova aula", tipo="Aula", redirect_name="estudos:aulas")


def aula_editar(request, item_id):
    item = get_object_or_404(Aula, id=item_id, usuario=request.user)
    return _form(request, AulaForm, titulo="Editar aula", tipo="Aula", instance=item, redirect_name="estudos:aulas")


def aula_detalhe(request, item_id):
    aula = get_object_or_404(
        Aula.objects.filter(usuario=request.user).select_related("disciplina", "disciplina__curso"),
        id=item_id,
    )
    return render(request, "estudos/aula_detalhe.html", {"aula": aula})


def confirmar_exclusao(request, tipo, item_id):
    configuracoes = {
        "curso": (Curso, "Curso", "estudos:cursos"),
        "disciplina": (Disciplina, "Disciplina", "estudos:disciplinas"),
        "aula": (Aula, "Conteúdo", "estudos:aulas"),
    }
    modelo, rotulo, retorno = configuracoes.get(tipo, (None, None, None))
    if modelo is None:
        return redirect("estudos:inicio")
    item = get_object_or_404(modelo, id=item_id, usuario=request.user)
    return render(
        request,
        "estudos/confirmar_exclusao.html",
        {"item": item, "tipo": tipo, "rotulo": rotulo, "retorno": retorno},
    )


@require_POST
def excluir(request, tipo, item_id):
    configuracoes = {
        "curso": (Curso, "Curso", "estudos:cursos"),
        "disciplina": (Disciplina, "Disciplina", "estudos:disciplinas"),
        "aula": (Aula, "Conteúdo", "estudos:aulas"),
    }
    modelo, rotulo, retorno = configuracoes.get(tipo, (None, None, None))
    if modelo is None:
        return redirect("estudos:inicio")
    item = get_object_or_404(modelo, id=item_id, usuario=request.user)
    try:
        item.delete()
    except ProtectedError:
        messages.error(
            request,
            (
                f"{rotulo} não pôde ser excluído porque possui informações "
                "relacionadas. Exclua primeiro os itens vinculados."
            ),
        )
    else:
        messages.success(request, f"{rotulo} excluído com sucesso.")
    return redirect(retorno)
