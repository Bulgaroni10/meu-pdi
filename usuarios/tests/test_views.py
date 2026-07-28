from django.test import TestCase
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

    def test_rota_de_login_nao_existe(self):
        response = self.client.get("/conta/login/")

        self.assertEqual(response.status_code, 404)
