import json

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from biblioteca.models import MaterialPDF
from estudos.models import Aula
from .forms import AnotacaoForm
from .models import Anotacao, VersaoAnotacao
from .services import autosalvar, criar_anotacao, restaurar_versao


def lista(request):
    notas = Anotacao.objects.filter(usuario=request.user).select_related(
        "aula", "aula__disciplina"
    )
    termo = request.GET.get("q", "").strip()
    if termo:
        notas = notas.filter(
            Q(conteudo_texto__icontains=termo) | Q(titulo__icontains=termo)
        )
    return render(request, "anotacoes/lista.html", {"anotacoes": notas, "q": termo})


def workspace_aula(request, aula_id):
    aula = get_object_or_404(Aula, id=aula_id, usuario=request.user)
    material = aula.materiais_pdf.filter(principal=True).first() or aula.materiais_pdf.first()
    return render(
        request, "anotacoes/workspace_aula.html",
        {"aula": aula, "material": material, "anotacoes": aula.anotacoes.all()},
    )


def criar(request):
    initial = {}
    if aula_id := request.GET.get("aula"):
        initial["aula"] = aula_id
    form = AnotacaoForm(request.POST or None, usuario=request.user, initial=initial)
    if request.method == "POST" and form.is_valid():
        nota = criar_anotacao(form, request.user)
        messages.success(request, "Anotação criada.")
        return redirect("anotacoes:editar", nota.id)
    return render(request, "anotacoes/form.html", {"form": form})


@ensure_csrf_cookie
def editar(request, anotacao_id):
    nota = get_object_or_404(
        Anotacao.objects.select_related("aula"), id=anotacao_id, usuario=request.user
    )
    material = nota.aula.materiais_pdf.filter(principal=True).first() or nota.aula.materiais_pdf.first()
    return render(request, "anotacoes/editar.html", {"anotacao": nota, "material": material})


@require_POST
def autosave(request, anotacao_id):
    nota = get_object_or_404(Anotacao, id=anotacao_id, usuario=request.user)
    try:
        dados = json.loads(request.body)
        pagina = int(dados["pagina"]) if dados.get("pagina") else None
        nota = autosalvar(
            nota, request.user, titulo=dados.get("titulo", ""),
            html=dados.get("conteudo_html", ""), pagina=pagina,
            versao_cliente=int(dados.get("versao", 0)),
        )
    except ValueError as exc:
        if str(exc) == "CONFLITO":
            return JsonResponse(
                {"erro": "A anotação mudou em outra aba.", "versao": nota.versao_atual},
                status=409,
            )
        return JsonResponse({"erro": "Dados inválidos."}, status=400)
    return JsonResponse({"salvo": True, "versao": nota.versao_atual})


@require_POST
def restaurar(request, anotacao_id, versao_id):
    nota = get_object_or_404(Anotacao, id=anotacao_id, usuario=request.user)
    versao = get_object_or_404(
        VersaoAnotacao, id=versao_id, anotacao=nota, usuario=request.user
    )
    restaurar_versao(nota, versao, request.user)
    messages.success(request, f"Versão {versao.numero} restaurada.")
    return redirect("anotacoes:editar", nota.id)
