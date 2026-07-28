from django.urls import path

from . import views

app_name = "competencias"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nova/", views.criar, name="criar"),
    path("<uuid:competencia_id>/", views.detalhe, name="detalhe"),
    path("<uuid:competencia_id>/editar/", views.editar, name="editar"),
    path("<uuid:competencia_id>/avaliar/", views.avaliar, name="avaliar"),
    path("<uuid:competencia_id>/arquivar/", views.arquivar, name="arquivar"),
]
