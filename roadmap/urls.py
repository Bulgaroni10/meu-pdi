from django.urls import path

from . import views

app_name = "roadmap"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("importar-pdf/", views.importar_pdf, name="importar_pdf"),
    path("<uuid:roadmap_id>/", views.detalhe, name="detalhe"),
    path(
        "<uuid:roadmap_id>/etapas/<uuid:etapa_id>/alternar/",
        views.etapa_alternar,
        name="etapa_alternar",
    ),
    path("fontes/<uuid:fonte_id>/abrir/", views.abrir_fonte, name="abrir_fonte"),
]
