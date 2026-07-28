import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from usuarios.models import PreferenciaUsuario, Usuario


class Command(BaseCommand):
    help = "Configura o usuário pessoal usando variáveis de ambiente."

    @transaction.atomic
    def handle(self, *args, **options):
        email = os.getenv("PDI_ADMIN_EMAIL", "").lower().strip()
        password = os.getenv("PDI_ADMIN_PASSWORD", "")
        nome = os.getenv("PDI_ADMIN_NAME", "Kauan Bulgaroni").strip()

        if not email or not password:
            if settings.PDI_REQUIRE_LOGIN:
                raise CommandError(
                    "Defina PDI_ADMIN_EMAIL e PDI_ADMIN_PASSWORD antes do deploy."
                )
            self.stdout.write(
                "Credenciais pessoais não configuradas; modo local automático mantido."
            )
            return

        usuario = Usuario.objects.filter(pk=1).first()
        if usuario is None:
            usuario = Usuario.objects.create_user(
                email=email,
                password=password,
                nome=nome,
                is_active=True,
            )
            senha_configurada = True
        else:
            usuario.email = email
            usuario.nome = nome or usuario.nome
            usuario.is_active = True
            senha_configurada = not usuario.has_usable_password()
            if senha_configurada:
                usuario.set_password(password)
            usuario.save()

        PreferenciaUsuario.objects.get_or_create(usuario=usuario)
        mensagem = "Usuário pessoal configurado"
        if senha_configurada:
            mensagem += " com senha inicial"
        else:
            mensagem += " sem substituir a senha atual"
        self.stdout.write(self.style.SUCCESS(f"{mensagem}."))
