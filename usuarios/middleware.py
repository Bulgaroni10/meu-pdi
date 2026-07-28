from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse

from .models import Usuario


class UsuarioPessoalMiddleware:
    """Exige login em produção ou abre o perfil automaticamente no uso local."""

    ROTAS_PUBLICAS = {
        "/conta/login/",
        "/health/live/",
        "/health/ready/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in self.ROTAS_PUBLICAS:
            return self.get_response(request)

        if request.user.is_authenticated:
            return self.get_response(request)

        if settings.PDI_REQUIRE_LOGIN:
            login_url = reverse("usuarios:login")
            query = urlencode({"next": request.get_full_path()})
            return redirect(f"{login_url}?{query}")

        usuario, created = Usuario.objects.get_or_create(
            pk=1,
            defaults={
                "email": "pessoal@meupdi.local",
                "nome": "Você",
                "is_active": True,
            },
        )
        if created:
            usuario.set_unusable_password()
            usuario.save(update_fields=["password", "updated_at"])
        login(
            request,
            usuario,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        return self.get_response(request)
