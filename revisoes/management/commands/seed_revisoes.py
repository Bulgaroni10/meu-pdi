from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from competencias.models import Competencia
from objetivos.models import Objetivo
from projetos.models import Projeto
from revisoes.models import AcaoRevisao, RevisaoPeriodica
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Cria uma revisão mensal demonstrativa com próximas ações."

    @transaction.atomic
    def handle(self, *args, **options):
        usuario = Usuario.objects.get(pk=1)
        hoje = timezone.localdate()
        inicio_mes = hoje.replace(day=1)
        revisao, _ = RevisaoPeriodica.objects.get_or_create(
            usuario=usuario,
            titulo=f"Revisão mensal — {hoje.strftime('%m/%Y')}",
            defaults={
                "tipo": RevisaoPeriodica.Tipo.MENSAL,
                "periodo_inicio": inicio_mes,
                "periodo_fim": hoje,
                "nota_periodo": 4,
                "conquistas": (
                    "Estruturei o PDI, avancei nos estudos de Azure e iniciei "
                    "um projeto prático documentado."
                ),
                "dificuldades": (
                    "Manter constância nos dias com maior volume de trabalho."
                ),
                "aprendizados": (
                    "Entregas pequenas e registradas tornam a evolução mais visível."
                ),
                "ajustes": (
                    "Reservar blocos curtos de estudo e concluir uma evidência por semana."
                ),
                "conclusao": (
                    "O ciclo teve avanço consistente e agora precisa de regularidade."
                ),
            },
        )
        acoes = (
            (
                "Concluir a próxima tarefa do laboratório Azure",
                {"projeto": Projeto.objects.filter(usuario=usuario).first()},
            ),
            (
                "Atualizar o progresso do objetivo profissional",
                {"objetivo": Objetivo.objects.filter(usuario=usuario).first()},
            ),
            (
                "Registrar nova evidência de PowerShell",
                {"competencia": Competencia.objects.filter(usuario=usuario).first()},
            ),
        )
        for descricao, vinculo in acoes:
            AcaoRevisao.objects.get_or_create(
                usuario=usuario,
                revisao=revisao,
                descricao=descricao,
                defaults={**vinculo, "prazo": hoje},
            )
        self.stdout.write(self.style.SUCCESS("Revisão demonstrativa pronta."))
