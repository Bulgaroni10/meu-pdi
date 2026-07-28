from django.core.management.base import BaseCommand
from django.db import transaction

from usuarios.models import PreferenciaUsuario, Usuario


class Command(BaseCommand):
    help = "Cria ou atualiza o usuário demonstrativo editável da fundação."

    def add_arguments(self, parser):
        parser.add_argument("--email", default="demo@meupdi.local")

    @transaction.atomic
    def handle(self, *args, **options):
        usuario, created = Usuario.objects.get_or_create(
            pk=1,
            defaults={
                "email": options["email"].lower(),
                "nome": "Kauan Bulgaroni",
                "cargo_atual": "Analista de Infraestrutura de TI",
                "cargo_desejado": (
                    "Analista de Infraestrutura Pleno — Cloud Azure e automação"
                ),
                "objetivo_principal": (
                    "Tornar-me Analista de Infraestrutura Pleno, com "
                    "especialização em Cloud Azure e automação, até dezembro de 2027."
                ),
            },
        )
        if not created:
            usuario.nome = "Kauan Bulgaroni"
            usuario.cargo_atual = "Analista de Infraestrutura de TI"
            usuario.cargo_desejado = (
                "Analista de Infraestrutura Pleno — Cloud Azure e automação"
            )
            usuario.objetivo_principal = (
                "Tornar-me Analista de Infraestrutura Pleno, com especialização "
                "em Cloud Azure e automação, até dezembro de 2027."
            )
            usuario.email = options["email"].lower()
        usuario.set_unusable_password()
        usuario.save()
        PreferenciaUsuario.objects.get_or_create(usuario=usuario)

        action = "criado" if created else "atualizado"
        self.stdout.write(self.style.SUCCESS(f"Usuário demonstrativo {action}."))
