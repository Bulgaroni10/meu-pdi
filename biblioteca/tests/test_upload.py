from io import BytesIO
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from pypdf import PdfWriter

from biblioteca.models import MaterialPDF
from estudos.models import Aula, Curso, Disciplina
from usuarios.models import Usuario


def pdf_valido():
    stream = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=400)
    writer.write(stream)
    return stream.getvalue()


class UploadPDFTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.temp.name)
        self.override.enable()
        self.usuario = Usuario.objects.create_user(
            id=1, email="pessoal@meupdi.local", nome="Você"
        )
        curso = Curso.objects.create(
            usuario=self.usuario, nome="Curso", tipo=Curso.Tipo.LIVRE
        )
        disciplina = Disciplina.objects.create(
            usuario=self.usuario, curso=curso, nome="Disciplina"
        )
        self.aula = Aula.objects.create(
            usuario=self.usuario, disciplina=disciplina, titulo="Aula"
        )

    def tearDown(self):
        self.override.disable()
        self.temp.cleanup()

    def test_upload_valida_e_armazena_pdf_na_aula(self):
        arquivo = SimpleUploadedFile(
            "material.pdf", pdf_valido(), content_type="application/pdf"
        )
        response = self.client.post(
            reverse("biblioteca:upload"),
            {
                "aula": str(self.aula.id),
                "titulo": "Material principal",
                "descricao": "",
                "arquivo": arquivo,
                "principal": "on",
            },
        )

        material = MaterialPDF.objects.get()
        self.assertRedirects(
            response, reverse("anotacoes:workspace_aula", args=[self.aula.id])
        )
        self.assertEqual(material.quantidade_paginas, 1)
        self.assertTrue(material.arquivo.name.startswith(f"usuarios/{self.usuario.id}/aulas/"))

    def test_arquivo_falso_e_recusado(self):
        arquivo = SimpleUploadedFile(
            "material.pdf", b"arquivo falso", content_type="application/pdf"
        )
        response = self.client.post(
            reverse("biblioteca:upload"),
            {"aula": self.aula.id, "titulo": "Falso", "arquivo": arquivo},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "assinatura")
        self.assertFalse(MaterialPDF.objects.exists())

    def test_pdf_protegido_pode_ser_exibido_no_visualizador_interno(self):
        arquivo = SimpleUploadedFile(
            "material.pdf", pdf_valido(), content_type="application/pdf"
        )
        self.client.post(
            reverse("biblioteca:upload"),
            {
                "aula": str(self.aula.id),
                "titulo": "Material principal",
                "descricao": "",
                "arquivo": arquivo,
                "principal": "on",
            },
        )
        material = MaterialPDF.objects.get()

        response = self.client.get(
            reverse("biblioteca:abrir", args=[material.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Frame-Options"], "SAMEORIGIN")
        self.assertEqual(response["Cache-Control"], "private, no-store")

    def test_upload_nao_fica_publico_em_rota_direta_de_media(self):
        arquivo = SimpleUploadedFile(
            "material.pdf", pdf_valido(), content_type="application/pdf"
        )
        self.client.post(
            reverse("biblioteca:upload"),
            {
                "aula": str(self.aula.id),
                "titulo": "Material privado",
                "descricao": "",
                "arquivo": arquivo,
            },
        )
        material = MaterialPDF.objects.get()

        response = self.client.get(material.arquivo.url)

        self.assertEqual(response.status_code, 404)
