from django.urls import path

from . import views

app_name = "estudos"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("trilhas/", views.trilhas, name="trilhas"),
    path("trilhas/nova/", views.trilha_criar, name="trilha_criar"),
    path("trilhas/<uuid:item_id>/editar/", views.trilha_editar, name="trilha_editar"),
    path("cursos/", views.cursos, name="cursos"),
    path("cursos/novo/", views.curso_criar, name="curso_criar"),
    path("cursos/<uuid:item_id>/", views.curso_detalhe, name="curso_detalhe"),
    path("cursos/<uuid:item_id>/editar/", views.curso_editar, name="curso_editar"),
    path("periodos/novo/", views.periodo_criar, name="periodo_criar"),
    path("disciplinas/", views.disciplinas, name="disciplinas"),
    path("disciplinas/nova/", views.disciplina_criar, name="disciplina_criar"),
    path("disciplinas/<uuid:item_id>/", views.disciplina_detalhe, name="disciplina_detalhe"),
    path("disciplinas/<uuid:item_id>/editar/", views.disciplina_editar, name="disciplina_editar"),
    path("aulas/", views.aulas, name="aulas"),
    path("aulas/nova/", views.aula_criar, name="aula_criar"),
    path("aulas/<uuid:item_id>/", views.aula_detalhe, name="aula_detalhe"),
    path("aulas/<uuid:item_id>/editar/", views.aula_editar, name="aula_editar"),
    path(
        "conclusao/<str:tipo>/<uuid:item_id>/alternar/",
        views.alternar_conclusao,
        name="alternar_conclusao",
    ),
    path(
        "sessoes/registrar/",
        views.registrar_sessao,
        name="registrar_sessao",
    ),
    path(
        "excluir/<str:tipo>/<uuid:item_id>/",
        views.confirmar_exclusao,
        name="confirmar_exclusao",
    ),
    path(
        "excluir/<str:tipo>/<uuid:item_id>/confirmar/",
        views.excluir,
        name="excluir",
    ),
]
