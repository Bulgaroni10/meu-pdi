from django.test import TestCase

from anotacoes.forms import AnotacaoForm
from anotacoes.models import VersaoAnotacao
from anotacoes.services import autosalvar, criar_anotacao
from estudos.models import Aula, Curso, Disciplina
from usuarios.models import Usuario


class AnotacaoServiceTests(TestCase):
    def setUp(self):
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

    def criar(self):
        form = AnotacaoForm(
            {
                "aula": self.aula.id,
                "titulo": "Resumo",
                "tipo": "resumo",
                "pagina_pdf": 2,
                "trecho_referencia": "",
                "favorita": "",
                "tags": "cloud",
                "conteudo_html": "<p><strong>Seguro</strong><script>alert(1)</script></p>",
            },
            usuario=self.usuario,
        )
        self.assertTrue(form.is_valid(), form.errors)
        return criar_anotacao(form, self.usuario)

    def test_sanitiza_html_e_cria_primeira_versao(self):
        nota = self.criar()

        self.assertNotIn("<script", nota.conteudo_html)
        self.assertIn("Seguro", nota.conteudo_texto)
        self.assertEqual(nota.versoes.count(), 1)

    def test_autosave_incrementa_versao(self):
        nota = self.criar()

        nota = autosalvar(
            nota, self.usuario, titulo="Novo título",
            html="<p>Conteúdo atualizado</p>", pagina=3, versao_cliente=1,
        )

        self.assertEqual(nota.versao_atual, 2)
        self.assertEqual(VersaoAnotacao.objects.count(), 2)

    def test_autosave_recusa_versao_desatualizada(self):
        nota = self.criar()

        with self.assertRaisesMessage(ValueError, "CONFLITO"):
            autosalvar(
                nota, self.usuario, titulo="Conflito", html="<p>x</p>",
                pagina=1, versao_cliente=0,
            )
