import json

from django.test import TestCase
from django.urls import reverse

from anotacoes.models import Anotacao
from estudos.models import Aula, Curso, Disciplina
from usuarios.models import Usuario


class AnotacaoViewTests(TestCase):
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

    def test_workspace_abre_sem_pdf(self):
        response = self.client.get(
            reverse("anotacoes:workspace_aula", args=[self.aula.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenhum PDF nesta aula")

    def test_cria_anotacao_e_abre_editor(self):
        response = self.client.post(
            reverse("anotacoes:criar"),
            {
                "aula": self.aula.id,
                "titulo": "Minha nota",
                "tipo": "geral",
                "pagina_pdf": 1,
                "trecho_referencia": "",
                "favorita": "",
                "tags": "",
                "conteudo_html": "<p>Conteúdo</p>",
            },
        )

        nota = Anotacao.objects.get()
        self.assertRedirects(
            response, reverse("anotacoes:editar", args=[nota.id])
        )

    def test_endpoint_autosave_retorna_nova_versao(self):
        nota = Anotacao.objects.create(
            usuario=self.usuario, aula=self.aula, titulo="Nota"
        )
        response = self.client.post(
            reverse("anotacoes:autosave", args=[nota.id]),
            data=json.dumps(
                {
                    "titulo": "Nota atualizada",
                    "conteudo_html": "<p>Texto</p>",
                    "pagina": 4,
                    "versao": 1,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["versao"], 2)
