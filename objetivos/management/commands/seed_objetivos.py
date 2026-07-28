from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from objetivos.models import HistoricoObjetivo, Objetivo, Tag
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Cria o objetivo profissional inicial de demonstração."

    @transaction.atomic
    def handle(self, *args, **options):
        usuario, created_user = Usuario.objects.get_or_create(
            pk=1,
            defaults={
                "email": "pessoal@meupdi.local",
                "nome": "Você",
            },
        )
        if created_user:
            usuario.set_unusable_password()
            usuario.save(update_fields=("password", "updated_at"))

        objetivo, created = Objetivo.objects.get_or_create(
            usuario=usuario,
            titulo=(
                "Tornar-me Analista de Infraestrutura Pleno com foco em "
                "Azure e automação"
            ),
            defaults={
                "descricao": (
                    "Consolidar competências técnicas e práticas para atuar com "
                    "mais autonomia em infraestrutura, cloud e ambientes híbridos."
                ),
                "categoria": Objetivo.Categoria.PROFISSIONAL,
                "motivo": (
                    "Ampliar minha capacidade de entregar soluções confiáveis, "
                    "automatizadas e alinhadas às necessidades do negócio."
                ),
                "data_inicio": date(2026, 1, 1),
                "prazo": date(2027, 12, 31),
                "prioridade": Objetivo.Prioridade.ALTA,
                "status": Objetivo.Status.EM_ANDAMENTO,
                "progresso": 10,
                "resultado_esperado": (
                    "Estar preparado para assumir uma posição de Analista de "
                    "Infraestrutura Pleno."
                ),
                "evidencia_esperada": (
                    "Projetos documentados, laboratórios Azure, automações e "
                    "resultados práticos registrados."
                ),
                "proxima_acao": (
                    "Mapear as lacunas atuais em Azure, PowerShell e automação."
                ),
            },
        )
        for nome, slug in (
            ("Carreira", "carreira"),
            ("Azure", "azure"),
            ("Automação", "automacao"),
        ):
            tag, _ = Tag.objects.get_or_create(
                usuario=usuario,
                slug=slug,
                defaults={"nome": nome},
            )
            objetivo.tags.add(tag)

        if created:
            HistoricoObjetivo.objects.create(
                objetivo=objetivo,
                usuario=usuario,
                tipo=HistoricoObjetivo.Tipo.CRIACAO,
                descricao="Objetivo demonstrativo criado.",
            )

        estado = "criado" if created else "já existia"
        self.stdout.write(self.style.SUCCESS(f"Objetivo demonstrativo {estado}."))
