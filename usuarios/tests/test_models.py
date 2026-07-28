from django.test import TestCase

from usuarios.models import Usuario


class UsuarioModelTests(TestCase):
    def test_cria_usuario_com_email_normalizado(self):
        usuario = Usuario.objects.create_user(
            email="Pessoa@EXAMPLE.COM",
            password="UmaSenhaForte123!",
            nome="Pessoa",
        )

        self.assertEqual(usuario.email, "pessoa@example.com")
        self.assertTrue(usuario.check_password("UmaSenhaForte123!"))
        self.assertFalse(usuario.is_staff)

    def test_email_e_obrigatorio(self):
        with self.assertRaisesMessage(ValueError, "O e-mail é obrigatório."):
            Usuario.objects.create_user(email="", password="senha")
