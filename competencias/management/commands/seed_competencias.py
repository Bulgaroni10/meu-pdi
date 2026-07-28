from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from competencias.models import (
    AvaliacaoCompetencia,
    Competencia,
    EvidenciaCompetencia,
)
from projetos.models import Evidencia
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Cria competências pessoais demonstrativas ligadas às evidências existentes."

    @transaction.atomic
    def handle(self, *args, **options):
        usuario = Usuario.objects.get(pk=1)
        evidencia = Evidencia.objects.filter(usuario=usuario).first()
        dados = (
            (
                "Microsoft Azure",
                4,
                "Provisionar, proteger e monitorar recursos de nuvem com autonomia.",
            ),
            (
                "PowerShell e automação",
                4,
                "Criar scripts reutilizáveis, seguros e documentados.",
            ),
            (
                "Documentação técnica",
                3,
                "Registrar decisões, execução, validação e aprendizados.",
            ),
        )
        for nome, meta, criterios in dados:
            competencia, _ = Competencia.objects.get_or_create(
                usuario=usuario,
                nome=nome,
                defaults={
                    "categoria": Competencia.Categoria.TECNICA,
                    "nivel_desejado": meta,
                    "criterios": criterios,
                },
            )
            if evidencia and not competencia.avaliacoes.exists():
                avaliacao = AvaliacaoCompetencia.objects.create(
                    usuario=usuario,
                    competencia=competencia,
                    nivel=1,
                    justificativa=(
                        "Primeira aplicação prática registrada no projeto pessoal."
                    ),
                    data=timezone.localdate(),
                )
                EvidenciaCompetencia.objects.create(
                    usuario=usuario,
                    avaliacao=avaliacao,
                    evidencia=evidencia,
                )
        self.stdout.write(self.style.SUCCESS("Competências demonstrativas prontas."))
