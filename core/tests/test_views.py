from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from objetivos.models import Objetivo
from usuarios.models import Usuario


class DashboardTests(TestCase):
    def test_dashboard_abre_direto_sem_login(self):
        response = self.client.get(reverse("core:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Olá, eu sou")

    def test_primeiro_acesso_cria_perfil_pessoal_sem_senha(self):
        self.assertFalse(Usuario.objects.exists())

        response = self.client.get(reverse("core:dashboard"))

        self.assertEqual(response.status_code, 200)
        usuario = Usuario.objects.get(pk=1)
        self.assertEqual(usuario.email, "pessoal@meupdi.local")
        self.assertFalse(usuario.has_usable_password())

    def test_dashboard_consolida_progresso_e_prazos_reais(self):
        self.client.get(reverse("core:dashboard"))
        usuario = Usuario.objects.get(pk=1)
        Objetivo.objects.create(
            usuario=usuario,
            titulo="Concluir especialização",
            status=Objetivo.Status.EM_ANDAMENTO,
            progresso=40,
            prazo=timezone.localdate() + timedelta(days=10),
            proxima_acao="Estudar o próximo módulo",
        )

        response = self.client.get(reverse("core:dashboard"))

        self.assertEqual(response.context["progresso_geral"]["valor"], 40)
        self.assertEqual(response.context["progresso_geral"]["cobertura"], 25)
        self.assertEqual(len(response.context["semanas_estudo"]), 8)
        self.assertContains(response, "Concluir especialização")
        self.assertContains(response, "Estudar o próximo módulo")
        self.assertEqual(response.context["periodo_pdi"]["restante"], "10d")

    def test_busca_global_encontra_apenas_dados_do_perfil_pessoal(self):
        self.client.get(reverse("core:dashboard"))
        usuario = Usuario.objects.get(pk=1)
        outro = Usuario.objects.create_user(
            email="outro@meupdi.local",
            nome="Outro",
        )
        Objetivo.objects.create(
            usuario=usuario,
            titulo="Dominar Azure",
            descricao="Estudar serviços de nuvem",
            data_inicio=timezone.localdate(),
        )
        Objetivo.objects.create(
            usuario=outro,
            titulo="Azure confidencial de outro perfil",
            data_inicio=timezone.localdate(),
        )

        response = self.client.get(reverse("core:busca"), {"q": "Azure"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_resultados"], 1)
        self.assertContains(response, "Dominar Azure")
        self.assertNotContains(response, "Azure confidencial de outro perfil")

    def test_busca_vazia_orienta_usuario_sem_listar_dados(self):
        response = self.client.get(reverse("core:busca"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_resultados"], 0)
        self.assertContains(response, "O que você procura?")

    def test_health_checks_nao_dependem_de_sessao(self):
        live = self.client.get(reverse("core:health_live"))
        ready = self.client.get(reverse("core:health_ready"))

        self.assertEqual(live.status_code, 200)
        self.assertEqual(ready.status_code, 200)
        self.assertEqual(live.json()["status"], "ok")
        self.assertIn("X-Request-ID", live.headers)
        self.assertFalse(Usuario.objects.exists())

    def test_cabecalhos_de_seguranca_sao_enviados(self):
        response = self.client.get(reverse("core:dashboard"))

        self.assertIn("Content-Security-Policy", response.headers)
        self.assertEqual(
            response.headers["Cross-Origin-Opener-Policy"], "same-origin"
        )
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

    @override_settings(PUBLIC_DEMO_MODE=True)
    def test_demo_publica_bloqueia_alteracoes(self):
        response = self.client.post(reverse("objetivos:criar"), {})

        self.assertEqual(response.status_code, 403)
        self.assertIn("somente leitura", response.json()["detail"])
        self.assertFalse(Usuario.objects.exists())
