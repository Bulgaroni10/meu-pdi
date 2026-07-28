from django.urls import path

from . import views

app_name = "biblioteca"
urlpatterns = [
    path("", views.lista, name="lista"),
    path("upload/", views.upload, name="upload"),
    path("<uuid:material_id>/abrir/", views.abrir, name="abrir"),
]
