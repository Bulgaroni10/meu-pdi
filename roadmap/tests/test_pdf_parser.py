from io import BytesIO

from django.test import SimpleTestCase
from pypdf import PdfWriter

from roadmap.pdf_parser import ErroLeituraPDF, extrair_pdf, identificar_secoes


class PDFParserTests(SimpleTestCase):
    def test_identifica_secoes_por_titulos(self):
        texto = """
        MÓDULO 1 - FUNDAMENTOS
        Conceitos de computação em nuvem, responsabilidades e modelos de serviço.
        Este conteúdo estabelece a base necessária para os próximos módulos.

        MÓDULO 2 - IDENTIDADE
        Microsoft Entra ID, usuários, grupos, funções e controle de acesso.
        Aplicar menor privilégio e revisar permissões é parte desta etapa.

        MÓDULO 3 - REDES
        Redes virtuais, sub-redes, rotas, DNS e grupos de segurança de rede.
        Construir um laboratório para validar a conectividade.
        """

        secoes = identificar_secoes(texto)

        self.assertEqual(len(secoes), 3)
        self.assertEqual(secoes[0].titulo, "MÓDULO 1 - FUNDAMENTOS")
        self.assertIn("Microsoft Entra ID", secoes[1].conteudo)

    def test_pdf_sem_texto_informa_necessidade_de_ocr(self):
        stream = BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        writer.write(stream)
        stream.seek(0)
        stream.name = "digitalizado.pdf"

        with self.assertRaisesMessage(ErroLeituraPDF, "precisam de OCR"):
            extrair_pdf(stream)
