from django.urls import path

from . import views

app_name = "anotacoes"
urlpatterns = [
    path("", views.lista, name="lista"),
    path("nova/", views.criar, name="criar"),
    path("aulas/<uuid:aula_id>/", views.workspace_aula, name="workspace_aula"),
    path("<uuid:anotacao_id>/", views.editar, name="editar"),
    path("<uuid:anotacao_id>/autosave/", views.autosave, name="autosave"),
    path("<uuid:anotacao_id>/versoes/<uuid:versao_id>/restaurar/", views.restaurar, name="restaurar"),
]
