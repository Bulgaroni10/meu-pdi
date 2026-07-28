from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from objetivos.models import Objetivo
from projetos.models import (
    Evidencia,
    MarcoProjeto,
    Projeto,
    ProjetoTecnologia,
    TarefaProjeto,
    Tecnologia,
)
from projetos.services import recalcular_progresso
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Cria um projeto pessoal demonstrativo de automação em Azure."

    @transaction.atomic
    def handle(self, *args, **options):
        usuario = Usuario.objects.get(pk=1)
        objetivo = Objetivo.objects.filter(usuario=usuario).first()
        projeto, _ = Projeto.objects.get_or_create(
            usuario=usuario,
            titulo="Laboratório de infraestrutura como código no Azure",
            defaults={
                "objetivo": objetivo,
                "problema": (
                    "Ambientes de laboratório configurados manualmente são lentos "
                    "e difíceis de reproduzir."
                ),
                "solucao": (
                    "Criar uma automação versionada para provisionar rede, máquinas "
                    "virtuais e monitoramento no Azure."
                ),
                "data_inicio": timezone.localdate(),
                "status": Projeto.Status.EM_ANDAMENTO,
                "repositorio_url": "https://github.com/",
            },
        )
        tarefas = (
            ("Desenhar a arquitetura do laboratório", TarefaProjeto.Status.CONCLUIDA),
            ("Automatizar rede e grupo de recursos", TarefaProjeto.Status.EM_ANDAMENTO),
            ("Documentar execução e validação", TarefaProjeto.Status.PENDENTE),
        )
        for ordem, (titulo, status) in enumerate(tarefas, start=1):
            TarefaProjeto.objects.get_or_create(
                usuario=usuario,
                projeto=projeto,
                ordem=ordem,
                defaults={"titulo": titulo, "status": status},
            )
        MarcoProjeto.objects.get_or_create(
            usuario=usuario,
            projeto=projeto,
            ordem=1,
            defaults={
                "titulo": "Primeiro ambiente reproduzível",
                "descricao": "Provisionamento completo executado sem configuração manual.",
            },
        )
        for nome, categoria in (
            ("Azure", Tecnologia.Categoria.NUVEM),
            ("PowerShell", Tecnologia.Categoria.LINGUAGEM),
            ("Bicep", Tecnologia.Categoria.FERRAMENTA),
        ):
            tecnologia, _ = Tecnologia.objects.get_or_create(
                usuario=usuario,
                nome=nome,
                defaults={"categoria": categoria},
            )
            ProjetoTecnologia.objects.get_or_create(
                usuario=usuario,
                projeto=projeto,
                tecnologia=tecnologia,
            )
        Evidencia.objects.get_or_create(
            usuario=usuario,
            projeto=projeto,
            titulo="Repositório inicial do laboratório",
            defaults={
                "tipo": Evidencia.Tipo.REPOSITORIO,
                "descricao": "Estrutura inicial versionada para acompanhar a evolução.",
                "url": projeto.repositorio_url,
            },
        )
        recalcular_progresso(projeto)
        self.stdout.write(self.style.SUCCESS("Projeto demonstrativo pronto."))
