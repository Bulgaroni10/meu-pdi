from django.urls import path

from . import views

app_name = "certificacoes"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nova/", views.criar, name="criar"),
    path("<uuid:certificacao_id>/", views.detalhe, name="detalhe"),
    path("<uuid:certificacao_id>/editar/", views.editar, name="editar"),
    path("<uuid:certificacao_id>/arquivar/", views.arquivar, name="arquivar"),
]
