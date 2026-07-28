from django.test import TestCase, override_settings
from django.urls import reverse

from usuarios.models import Usuario


class AcessoPessoalTests(TestCase):
    def test_perfil_abre_direto_sem_login(self):
        response = self.client.get(reverse("usuarios:perfil"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 1)

    def test_perfil_pessoal_pode_ser_atualizado(self):
        self.client.get(reverse("usuarios:perfil"))
        usuario = Usuario.objects.get(pk=1)

        response = self.client.post(
            reverse("usuarios:perfil"),
            {
                "nome": "Nome Atualizado",
                "email": usuario.email,
                "cargo_atual": "Analista",
                "cargo_desejado": "Analista Pleno",
                "objetivo_principal": "Evoluir",
                "timezone": "America/Sao_Paulo",
                "idioma": "pt-br",
                "tema": "escuro",
            },
        )

        self.assertRedirects(response, reverse("usuarios:perfil"))
        usuario.refresh_from_db()
        self.assertEqual(usuario.nome, "Nome Atualizado")
        self.assertEqual(Usuario.objects.count(), 1)

    def test_rota_de_login_existe(self):
        response = self.client.get(reverse("usuarios:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bem-vindo de volta")


@override_settings(PDI_REQUIRE_LOGIN=True, PUBLIC_DEMO_MODE=False)
class AutenticacaoPessoalTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email="kauan@example.com",
            password="Senha-forte-para-testes-2026",
            nome="Kauan",
        )

    def test_tela_privada_redireciona_para_login_preservando_destino(self):
        response = self.client.get(reverse("usuarios:perfil"))

        self.assertRedirects(
            response,
            f"{reverse('usuarios:login')}?next={reverse('usuarios:perfil')}",
            fetch_redirect_response=False,
        )

    def test_login_com_email_e_senha_abre_dashboard(self):
        response = self.client.post(
            reverse("usuarios:login"),
            {
                "username": self.usuario.email,
                "password": "Senha-forte-para-testes-2026",
                "lembrar": "1",
            },
        )

        self.assertRedirects(response, reverse("core:dashboard"))
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.usuario.pk,
        )
        self.assertFalse(self.client.session.get_expire_at_browser_close())

    def test_login_invalido_nao_revela_qual_campo_falhou(self):
        response = self.client.post(
            reverse("usuarios:login"),
            {
                "username": self.usuario.email,
                "password": "senha-incorreta",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "E-mail ou senha inválidos")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_encerra_sessao(self):
        self.client.force_login(self.usuario)

        response = self.client.post(reverse("usuarios:logout"))

        self.assertRedirects(response, reverse("usuarios:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_health_check_continua_publico(self):
        response = self.client.get(reverse("core:health_ready"))

        self.assertEqual(response.status_code, 200)
