from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from anotacoes.models import Anotacao
from biblioteca.models import MaterialPDF
from certificacoes.models import Certificacao
from competencias.models import (
    AvaliacaoCompetencia,
    Competencia,
    EvidenciaCompetencia,
)
from estudos.models import Aula, Curso, Disciplina, Periodo, SessaoEstudo, Trilha
from objetivos.models import Objetivo, Tag
from projetos.models import (
    Evidencia,
    MarcoProjeto,
    Projeto,
    ProjetoTecnologia,
    TarefaProjeto,
    Tecnologia,
)
from revisoes.models import AcaoRevisao, RevisaoPeriodica
from roadmap.models import FonteRoadmap, Roadmap
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Apaga todo o conteúdo do PDI, preservando a conta e a senha do usuário."

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirma a exclusão definitiva dos conteúdos.",
        )
        parser.add_argument(
            "--user-id",
            type=int,
            default=1,
            help="ID do usuário pessoal a ser limpo (padrão: 1).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["confirm"]:
            raise CommandError("Use --confirm para autorizar a exclusão dos dados.")

        usuario = Usuario.objects.filter(pk=options["user_id"]).first()
        if usuario is None:
            raise CommandError("Usuário pessoal não encontrado.")

        arquivos = self._collect_files(usuario)
        self._delete_content(usuario)
        self._clear_profile(usuario)

        def remove_files():
            for storage, name in arquivos:
                if name and storage.exists(name):
                    storage.delete(name)

        transaction.on_commit(remove_files)
        self.stdout.write(
            self.style.SUCCESS(
                f"PDI de {usuario.email} limpo; conta e senha foram preservadas."
            )
        )

    @staticmethod
    def _collect_files(usuario):
        arquivos = []
        for item in MaterialPDF.objects.filter(usuario=usuario):
            if item.arquivo.name:
                arquivos.append((item.arquivo.storage, item.arquivo.name))
        for item in Evidencia.objects.filter(usuario=usuario):
            if item.imagem.name:
                arquivos.append((item.imagem.storage, item.imagem.name))
        for item in FonteRoadmap.objects.filter(usuario=usuario):
            if item.arquivo.name:
                arquivos.append((item.arquivo.storage, item.arquivo.name))
        return arquivos

    @staticmethod
    def _delete_content(usuario):
        AcaoRevisao.objects.filter(usuario=usuario).delete()
        RevisaoPeriodica.objects.filter(usuario=usuario).delete()
        EvidenciaCompetencia.objects.filter(usuario=usuario).delete()
        AvaliacaoCompetencia.objects.filter(usuario=usuario).delete()
        Competencia.objects.filter(usuario=usuario).delete()
        Certificacao.objects.filter(usuario=usuario).delete()
        Anotacao.objects.filter(usuario=usuario).delete()
        MaterialPDF.objects.filter(usuario=usuario).delete()
        Evidencia.objects.filter(usuario=usuario).delete()
        ProjetoTecnologia.objects.filter(usuario=usuario).delete()
        TarefaProjeto.objects.filter(usuario=usuario).delete()
        MarcoProjeto.objects.filter(usuario=usuario).delete()
        Projeto.objects.filter(usuario=usuario).delete()
        Tecnologia.objects.filter(usuario=usuario).delete()
        Roadmap.objects.filter(usuario=usuario).delete()
        FonteRoadmap.objects.filter(usuario=usuario).delete()
        SessaoEstudo.objects.filter(usuario=usuario).delete()
        Aula.objects.filter(usuario=usuario).delete()
        Disciplina.objects.filter(usuario=usuario).delete()
        Periodo.objects.filter(usuario=usuario).delete()
        Curso.objects.filter(usuario=usuario).delete()
        Trilha.objects.filter(usuario=usuario).delete()
        Objetivo.objects.filter(usuario=usuario).delete()
        Tag.objects.filter(usuario=usuario).delete()

    @staticmethod
    def _clear_profile(usuario):
        usuario.cargo_atual = ""
        usuario.cargo_desejado = ""
        usuario.resumo_profissional = ""
        usuario.objetivo_principal = ""
        usuario.localizacao = ""
        usuario.github_url = ""
        usuario.linkedin_url = ""
        usuario.save(
            update_fields=[
                "cargo_atual",
                "cargo_desejado",
                "resumo_profissional",
                "objetivo_principal",
                "localizacao",
                "github_url",
                "linkedin_url",
                "updated_at",
            ]
        )
