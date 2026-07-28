from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from usuarios.models import Usuario


class EnsurePersonalUserCommandTests(TestCase):
    @override_settings(PDI_REQUIRE_LOGIN=True)
    @patch.dict(
        "os.environ",
        {
            "PDI_ADMIN_EMAIL": "kauan@example.com",
            "PDI_ADMIN_PASSWORD": "Senha-inicial-segura-2026",
            "PDI_ADMIN_NAME": "Kauan Bulgaroni",
        },
    )
    def test_configura_senha_inicial_sem_substituir_senha_posterior(self):
        usuario = Usuario.objects.create_user(
            email="demo@meupdi.local",
            password=None,
            nome="Demo",
        )

        call_command("ensure_personal_user")
        usuario.refresh_from_db()

        self.assertEqual(usuario.email, "kauan@example.com")
        self.assertTrue(usuario.check_password("Senha-inicial-segura-2026"))

        usuario.set_password("Senha-alterada-pelo-usuario-2026")
        usuario.save(update_fields=["password"])
        call_command("ensure_personal_user")
        usuario.refresh_from_db()

        self.assertTrue(usuario.check_password("Senha-alterada-pelo-usuario-2026"))
