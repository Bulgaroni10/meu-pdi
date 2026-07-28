"""Configurações para desenvolvimento local."""

from .base import *  # noqa: F403

DEBUG = True
SECRET_KEY = os.getenv(  # noqa: F405
    "DJANGO_SECRET_KEY", "django-insecure-local-meu-pdi"
)

# Facilita testes locais sem depender do arquivo manifestado do collectstatic.
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
}
