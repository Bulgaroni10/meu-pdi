from django.urls import path

from . import views

app_name = "revisoes"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nova/", views.criar, name="criar"),
    path("<uuid:revisao_id>/", views.detalhe, name="detalhe"),
    path("<uuid:revisao_id>/editar/", views.editar, name="editar"),
    path("<uuid:revisao_id>/concluir/", views.concluir, name="concluir"),
    path("<uuid:revisao_id>/acoes/nova/", views.acao_criar, name="acao_criar"),
    path(
        "<uuid:revisao_id>/acoes/<uuid:acao_id>/alternar/",
        views.acao_alternar,
        name="acao_alternar",
    ),
]
