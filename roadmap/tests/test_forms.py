from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from roadmap.forms import ImportarRoadmapPDFForm
from usuarios.models import Usuario


class ImportarRoadmapPDFFormTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            nome="Você",
        )

    def test_recusa_arquivo_com_assinatura_invalida(self):
        arquivo = SimpleUploadedFile(
            "material.pdf",
            b"nao e um pdf",
            content_type="application/pdf",
        )

        form = ImportarRoadmapPDFForm(
            files={"pdf": arquivo},
            usuario=self.usuario,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("assinatura", form.errors["pdf"][0])

    def test_recusa_extensao_diferente_de_pdf(self):
        arquivo = SimpleUploadedFile(
            "material.txt",
            b"%PDF-1.7",
            content_type="application/pdf",
        )

        form = ImportarRoadmapPDFForm(
            files={"pdf": arquivo},
            usuario=self.usuario,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("extensão", form.errors["pdf"][0])
