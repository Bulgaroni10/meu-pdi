from django.contrib.auth import login

from .models import Usuario


class UsuarioPessoalMiddleware:
    """Abre o sistema sempre com o único perfil pessoal local."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/health/"):
            return self.get_response(request)
        if not request.user.is_authenticated:
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
