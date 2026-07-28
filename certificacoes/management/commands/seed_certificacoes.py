from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from certificacoes.models import Certificacao
from estudos.models import Trilha
from objetivos.models import Objetivo
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Cria o planejamento demonstrativo da certificação AZ-104."

    @transaction.atomic
    def handle(self, *args, **options):
        usuario = Usuario.objects.get(pk=1)
        hoje = timezone.localdate()
        Certificacao.objects.get_or_create(
            usuario=usuario,
            codigo="AZ-104",
            defaults={
                "nome": "Microsoft Azure Administrator Associate",
                "instituicao": "Microsoft",
                "status": Certificacao.Status.PREPARANDO,
                "prioridade": Certificacao.Prioridade.ALTA,
                "progresso": 20,
                "data_inicio": hoje,
                "data_prova": hoje + timedelta(days=90),
                "custo_previsto": 600,
                "objetivo": Objetivo.objects.filter(usuario=usuario).first(),
                "trilha": Trilha.objects.filter(usuario=usuario).first(),
                "url_oficial": (
                    "https://learn.microsoft.com/credentials/certifications/"
                    "azure-administrator/"
                ),
                "observacoes": (
                    "Priorizar identidade, governança, armazenamento, computação "
                    "e redes virtuais."
                ),
            },
        )
        self.stdout.write(self.style.SUCCESS("Certificação demonstrativa pronta."))
