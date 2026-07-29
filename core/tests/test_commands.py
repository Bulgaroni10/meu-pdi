from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from estudos.models import Aula, Curso, Disciplina
from objetivos.models import Objetivo
from projetos.models import Projeto
from roadmap.models import EtapaRoadmap, FaseRoadmap, Roadmap
from usuarios.models import Usuario


class ReplaceCloudPlanCommandTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            password="senha-de-teste",
            nome="Kauan",
        )

    def test_exige_confirmacao_explicita(self):
        with self.assertRaises(CommandError):
            call_command("replace_pdi_cloud_plan")

    def test_substitui_dados_pelo_plano_de_48_semanas(self):
        Objetivo.objects.create(
            usuario=self.usuario,
            titulo="Conteúdo antigo",
        )

        call_command("replace_pdi_cloud_plan", "--confirm")

        self.assertFalse(
            Objetivo.objects.filter(usuario=self.usuario, titulo="Conteúdo antigo").exists()
        )
        self.assertEqual(Roadmap.objects.filter(usuario=self.usuario).count(), 1)
        self.assertEqual(FaseRoadmap.objects.filter(usuario=self.usuario).count(), 12)
        self.assertEqual(EtapaRoadmap.objects.filter(usuario=self.usuario).count(), 48)
        self.assertEqual(Projeto.objects.filter(usuario=self.usuario).count(), 8)
        self.assertEqual(Curso.objects.filter(usuario=self.usuario).count(), 1)
        self.assertEqual(Disciplina.objects.filter(usuario=self.usuario).count(), 12)
        self.assertEqual(Aula.objects.filter(usuario=self.usuario).count(), 48)

    def test_novo_deploy_preserva_progresso_do_plano(self):
        call_command("replace_pdi_cloud_plan", "--confirm")
        etapa = EtapaRoadmap.objects.filter(usuario=self.usuario).first()
        etapa.concluida = True
        etapa.save()

        call_command("replace_pdi_cloud_plan", "--confirm")

        etapa.refresh_from_db()
        self.assertTrue(etapa.concluida)

    def test_substitui_estrutura_demonstrativa_completa(self):
        for command in (
            "seed_objetivos",
            "seed_estudos",
            "seed_anotacoes",
            "seed_projetos",
            "seed_competencias",
            "seed_revisoes",
            "seed_certificacoes",
        ):
            call_command(command)

        call_command("replace_pdi_cloud_plan", "--confirm")

        self.assertEqual(EtapaRoadmap.objects.filter(usuario=self.usuario).count(), 48)
        self.assertEqual(Projeto.objects.filter(usuario=self.usuario).count(), 8)
        self.assertEqual(Aula.objects.filter(usuario=self.usuario).count(), 48)


class ResetPdiDataCommandTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            password="senha-preservada",
            nome="Kauan",
            cargo_atual="Analista",
            github_url="https://github.com/exemplo",
        )

    def test_exige_confirmacao_explicita(self):
        with self.assertRaises(CommandError):
            call_command("reset_pdi_data")

    def test_limpa_conteudo_e_perfil_sem_apagar_conta_ou_senha(self):
        Objetivo.objects.create(usuario=self.usuario, titulo="Meta antiga")
        senha_anterior = self.usuario.password

        call_command("reset_pdi_data", "--confirm")

        self.usuario.refresh_from_db()
        self.assertFalse(Objetivo.objects.filter(usuario=self.usuario).exists())
        self.assertEqual(self.usuario.password, senha_anterior)
        self.assertEqual(self.usuario.cargo_atual, "")
        self.assertEqual(self.usuario.github_url, "")
        self.assertEqual(self.usuario.nome, "Kauan")
        self.assertEqual(self.usuario.email, "pessoal@meupdi.local")
