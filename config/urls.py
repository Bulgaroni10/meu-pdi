"""Rotas principais do Meu PDI."""

from django.urls import include, path

urlpatterns = [
    path("conta/", include("usuarios.urls")),
    path("objetivos/", include("objetivos.urls")),
    path("roadmaps/", include("roadmap.urls")),
    path("estudos/", include("estudos.urls")),
    path("biblioteca/", include("biblioteca.urls")),
    path("anotacoes/", include("anotacoes.urls")),
    path("projetos/", include("projetos.urls")),
    path("competencias/", include("competencias.urls")),
    path("revisoes/", include("revisoes.urls")),
    path("certificacoes/", include("certificacoes.urls")),
    path("indicadores/", include("indicadores.urls")),
    path("", include("core.urls")),
]
