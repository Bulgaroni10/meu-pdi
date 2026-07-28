from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from objetivos.models import Objetivo
from roadmap.models import EtapaRoadmap, FaseRoadmap, Roadmap
from roadmap.pdf_parser import DocumentoExtraido, SecaoPDF
from usuarios.models import Usuario


class RoadmapViewTests(TestCase):
    def setUp(self):
        self.temp_media = TemporaryDirectory()
        self.override_media = override_settings(MEDIA_ROOT=self.temp_media.name)
        self.override_media.enable()
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            nome="Você",
        )

    def tearDown(self):
        self.override_media.disable()
        self.temp_media.cleanup()

    def documento_extraido(self):
        return DocumentoExtraido(
            titulo="Guia de Azure",
            paginas=12,
            texto="Conteúdo extraído do documento.",
            secoes=[
                SecaoPDF(
                    titulo="Módulo 1 - Fundamentos",
                    conteudo=(
                        "Compreender modelos de nuvem e responsabilidades. "
                        "Criar um resumo comparativo dos serviços."
                    ),
                ),
                SecaoPDF(
                    titulo="Módulo 2 - Identidade",
                    conteudo=(
                        "Configurar usuários e grupos no Microsoft Entra ID. "
                        "Aplicar funções e menor privilégio."
                    ),
                ),
            ],
        )

    def arquivo_pdf(self):
        return SimpleUploadedFile(
            "guia-azure.pdf",
            b"%PDF-1.7\nconteudo de teste",
            content_type="application/pdf",
        )

    def test_tela_de_importacao_abre_direto(self):
        response = self.client.get(reverse("roadmap:importar_pdf"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Transforme um PDF em roadmap")

    @patch("roadmap.services.extrair_pdf")
    def test_upload_cria_roadmap_fases_etapas_e_entregas(self, extrair_mock):
        extrair_mock.return_value = self.documento_extraido()

        response = self.client.post(
            reverse("roadmap:importar_pdf"),
            {"pdf": self.arquivo_pdf(), "nome": "", "objetivo": ""},
        )

        roadmap = Roadmap.objects.get()
        self.assertRedirects(
            response,
            reverse("roadmap:detalhe", args=[roadmap.id]),
        )
        self.assertEqual(roadmap.nome, "Guia de Azure")
        self.assertEqual(roadmap.fases.count(), 2)
        self.assertGreaterEqual(roadmap.fases.first().etapas.count(), 1)
        self.assertEqual(roadmap.fases.first().entregas.count(), 1)
        self.assertTrue(roadmap.fonte_pdf.arquivo.name.endswith(".pdf"))

    @patch("roadmap.services.extrair_pdf")
    def test_pdf_fica_acessivel_apenas_pelo_perfil_pessoal(self, extrair_mock):
        extrair_mock.return_value = self.documento_extraido()
        self.client.post(
            reverse("roadmap:importar_pdf"),
            {"pdf": self.arquivo_pdf(), "nome": "", "objetivo": ""},
        )
        roadmap = Roadmap.objects.get()

        response = self.client.get(
            reverse("roadmap:abrir_fonte", args=[roadmap.fonte_pdf.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["X-Frame-Options"], "SAMEORIGIN")
        self.assertEqual(response["Cache-Control"], "private, no-store")

    def test_concluir_etapa_atualiza_fase_e_roadmap(self):
        objetivo = Objetivo.objects.create(
            usuario=self.usuario,
            titulo="Concluir o plano",
        )
        roadmap = Roadmap.objects.create(
            usuario=self.usuario,
            nome="Roadmap pessoal",
            objetivo=objetivo,
        )
        fase = FaseRoadmap.objects.create(
            usuario=self.usuario,
            roadmap=roadmap,
            titulo="Fundamentos",
            ordem=1,
        )
        etapa = EtapaRoadmap.objects.create(
            usuario=self.usuario,
            fase=fase,
            titulo="Estudar fundamentos",
            ordem=1,
        )

        response = self.client.post(
            reverse("roadmap:etapa_alternar", args=[roadmap.id, etapa.id])
        )

        self.assertRedirects(
            response, reverse("roadmap:detalhe", args=[roadmap.id])
        )
        etapa.refresh_from_db()
        fase.refresh_from_db()
        roadmap.refresh_from_db()
        objetivo.refresh_from_db()
        self.assertTrue(etapa.concluida)
        self.assertEqual(fase.progresso, 100)
        self.assertEqual(fase.status, FaseRoadmap.Status.CONCLUIDA)
        self.assertEqual(roadmap.status, Roadmap.Status.CONCLUIDO)
        self.assertEqual(objetivo.progresso, 100)
        self.assertEqual(objetivo.status, Objetivo.Status.CONCLUIDO)
