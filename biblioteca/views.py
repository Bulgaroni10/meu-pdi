from pathlib import Path

from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .forms import MaterialPDFForm
from .models import MaterialPDF
from .services import salvar_pdf


def lista(request):
    materiais = MaterialPDF.objects.filter(usuario=request.user).select_related(
        "aula", "aula__disciplina"
    )
    return render(request, "biblioteca/lista.html", {"materiais": materiais})


def upload(request):
    initial = {}
    if aula_id := request.GET.get("aula"):
        initial["aula"] = aula_id
    form = MaterialPDFForm(
        request.POST or None,
        request.FILES or None,
        usuario=request.user,
        initial=initial,
    )
    if request.method == "POST" and form.is_valid():
        material = salvar_pdf(form, request.user)
        messages.success(request, "PDF anexado à aula.")
        return redirect("anotacoes:workspace_aula", material.aula_id)
    return render(request, "biblioteca/upload.html", {"form": form})


@xframe_options_sameorigin
def abrir(request, material_id):
    material = get_object_or_404(
        MaterialPDF, id=material_id, usuario=request.user
    )
    response = FileResponse(material.arquivo.open("rb"), content_type="application/pdf")
    nome = Path(material.nome_original).name.replace('"', "")
    response["Content-Disposition"] = f'inline; filename="{nome}"'
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
