from django.urls import path

from . import views

app_name = "projetos"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.criar, name="criar"),
    path("<uuid:projeto_id>/", views.detalhe, name="detalhe"),
    path("<uuid:projeto_id>/editar/", views.editar, name="editar"),
    path("<uuid:projeto_id>/arquivar/", views.arquivar, name="arquivar"),
    path("<uuid:projeto_id>/marcos/novo/", views.marco_criar, name="marco_criar"),
    path(
        "<uuid:projeto_id>/marcos/<uuid:marco_id>/alternar/",
        views.marco_alternar,
        name="marco_alternar",
    ),
    path("<uuid:projeto_id>/tarefas/nova/", views.tarefa_criar, name="tarefa_criar"),
    path(
        "<uuid:projeto_id>/tarefas/<uuid:tarefa_id>/alternar/",
        views.tarefa_alternar,
        name="tarefa_alternar",
    ),
    path(
        "<uuid:projeto_id>/tecnologias/adicionar/",
        views.tecnologia_adicionar,
        name="tecnologia_adicionar",
    ),
    path(
        "<uuid:projeto_id>/evidencias/nova/",
        views.evidencia_criar,
        name="evidencia_criar",
    ),
    path(
        "<uuid:projeto_id>/evidencias/<uuid:evidencia_id>/editar/",
        views.evidencia_editar,
        name="evidencia_editar",
    ),
    path(
        "<uuid:projeto_id>/evidencias/<uuid:evidencia_id>/excluir/",
        views.evidencia_confirmar_exclusao,
        name="evidencia_confirmar_exclusao",
    ),
    path(
        "<uuid:projeto_id>/evidencias/<uuid:evidencia_id>/excluir/confirmar/",
        views.evidencia_excluir,
        name="evidencia_excluir",
    ),
    path(
        "<uuid:projeto_id>/evidencias/<uuid:evidencia_id>/imagem/",
        views.evidencia_imagem,
        name="evidencia_imagem",
    ),
]
