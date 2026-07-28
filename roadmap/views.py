from pathlib import Path

from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from objetivos.models import Objetivo

from .forms import ImportarRoadmapPDFForm
from .models import EtapaRoadmap, FonteRoadmap
from .pdf_parser import ErroLeituraPDF
from .selectors import roadmaps_do_usuario
from .services import criar_roadmap_do_pdf, recalcular_progresso_fase


def lista(request):
    roadmaps = roadmaps_do_usuario(request.user)
    return render(request, "roadmap/lista.html", {"roadmaps": roadmaps})


def importar_pdf(request):
    if request.method == "POST":
        form = ImportarRoadmapPDFForm(
            request.POST,
            request.FILES,
            usuario=request.user,
        )
        if form.is_valid():
            try:
                roadmap = criar_roadmap_do_pdf(
                    usuario=request.user,
                    arquivo=form.cleaned_data["pdf"],
                    nome=form.cleaned_data["nome"],
                    objetivo=form.cleaned_data["objetivo"],
                )
            except ErroLeituraPDF as exc:
                form.add_error("pdf", str(exc))
            else:
                messages.success(
                    request,
                    (
                        f"Roadmap criado com {roadmap.fases.count()} fases. "
                        "Revise o rascunho antes de começar."
                    ),
                )
                return redirect("roadmap:detalhe", roadmap.id)
    else:
        inicial = {}
        if objetivo_id := request.GET.get("objetivo"):
            objetivo = Objetivo.objects.filter(
                usuario=request.user,
                id=objetivo_id,
                arquivado_em__isnull=True,
            ).first()
            if objetivo:
                inicial["objetivo"] = objetivo
        form = ImportarRoadmapPDFForm(usuario=request.user, initial=inicial)
    return render(request, "roadmap/importar_pdf.html", {"form": form})


def detalhe(request, roadmap_id):
    roadmap = get_object_or_404(
        roadmaps_do_usuario(request.user),
        id=roadmap_id,
    )
    return render(request, "roadmap/detalhe.html", {"roadmap": roadmap})


@require_POST
def etapa_alternar(request, roadmap_id, etapa_id):
    roadmap = get_object_or_404(roadmaps_do_usuario(request.user), id=roadmap_id)
    etapa = get_object_or_404(
        EtapaRoadmap.objects.select_related("fase", "fase__roadmap"),
        id=etapa_id,
        fase__roadmap=roadmap,
        usuario=request.user,
    )
    etapa.concluida = not etapa.concluida
    etapa.save(update_fields=("concluida", "updated_at"))
    recalcular_progresso_fase(etapa.fase)
    messages.success(
        request,
        "Etapa marcada como concluída." if etapa.concluida else "Etapa reaberta.",
    )
    return redirect("roadmap:detalhe", roadmap_id=roadmap.id)


@xframe_options_sameorigin
def abrir_fonte(request, fonte_id):
    fonte = get_object_or_404(
        FonteRoadmap.objects.filter(usuario=request.user),
        id=fonte_id,
    )
    resposta = FileResponse(
        fonte.arquivo.open("rb"),
        content_type="application/pdf",
    )
    nome = Path(fonte.nome_original).name.replace('"', "")
    resposta["Content-Disposition"] = f'inline; filename="{nome}"'
    resposta["Cache-Control"] = "private, no-store"
    resposta["X-Content-Type-Options"] = "nosniff"
    return resposta
