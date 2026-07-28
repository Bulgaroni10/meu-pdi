from django.urls import path

from . import views

app_name = "objetivos"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.criar, name="criar"),
    path("<uuid:objetivo_id>/", views.detalhe, name="detalhe"),
    path("<uuid:objetivo_id>/editar/", views.editar, name="editar"),
    path("<uuid:objetivo_id>/arquivar/", views.arquivar, name="arquivar"),
    path("<uuid:objetivo_id>/restaurar/", views.restaurar, name="restaurar"),
]
