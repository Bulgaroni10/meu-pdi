from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from projetos.models import Evidencia, Projeto, TarefaProjeto, Tecnologia
from usuarios.models import Usuario


class ProjetoViewTests(TestCase):
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

    def criar_projeto(self, **kwargs):
        dados = {
            "usuario": self.usuario,
            "titulo": "Laboratório Azure pessoal",
            "data_inicio": timezone.localdate(),
            "status": Projeto.Status.EM_ANDAMENTO,
        }
        dados.update(kwargs)
        return Projeto.objects.create(**dados)

    def dados_projeto(self, **kwargs):
        dados = {
            "titulo": "Automação de infraestrutura",
            "objetivo": "",
            "problema": "Configuração manual e repetitiva",
            "solucao": "Automatizar o provisionamento",
            "data_inicio": timezone.localdate().isoformat(),
            "prazo": "",
            "status": Projeto.Status.EM_ANDAMENTO,
            "progresso": 10,
            "resultado": "",
            "aprendizados": "",
            "repositorio_url": "",
            "demonstracao_url": "",
        }
        dados.update(kwargs)
        return dados

    def test_lista_abre_sem_login(self):
        response = self.client.get(reverse("projetos:lista"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Meus projetos")

    def test_cria_projeto_para_perfil_pessoal(self):
        response = self.client.post(reverse("projetos:criar"), self.dados_projeto())

        projeto = Projeto.objects.get()
        self.assertRedirects(
            response, reverse("projetos:detalhe", args=[projeto.id])
        )
        self.assertEqual(projeto.usuario, self.usuario)
        self.assertEqual(projeto.progresso, 10)

    def test_projeto_de_outro_usuario_retorna_404(self):
        outro = Usuario.objects.create_user(
            email="outro@meupdi.local",
            nome="Outro",
        )
        projeto = Projeto.objects.create(
            usuario=outro,
            titulo="Projeto alheio",
            data_inicio=timezone.localdate(),
        )

        response = self.client.get(
            reverse("projetos:detalhe", args=[projeto.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_tarefa_concluida_atualiza_progresso_do_projeto(self):
        projeto = self.criar_projeto()
        response = self.client.post(
            reverse("projetos:tarefa_criar", args=[projeto.id]),
            {
                "titulo": "Criar ambiente",
                "descricao": "",
                "prazo": "",
                "status": TarefaProjeto.Status.PENDENTE,
                "prioridade": TarefaProjeto.Prioridade.ALTA,
            },
        )
        tarefa = TarefaProjeto.objects.get()
        self.assertRedirects(
            response, reverse("projetos:detalhe", args=[projeto.id])
        )

        self.client.post(
            reverse("projetos:tarefa_alternar", args=[projeto.id, tarefa.id])
        )

        projeto.refresh_from_db()
        self.assertEqual(projeto.progresso, 100)
        self.assertEqual(projeto.status, Projeto.Status.CONCLUIDO)

    def test_tecnologia_existente_nao_e_duplicada(self):
        projeto = self.criar_projeto()
        Tecnologia.objects.create(
            usuario=self.usuario,
            nome="Python",
            categoria=Tecnologia.Categoria.LINGUAGEM,
        )

        for nome in ("python", "PYTHON"):
            self.client.post(
                reverse("projetos:tecnologia_adicionar", args=[projeto.id]),
                {
                    "nome": nome,
                    "categoria": Tecnologia.Categoria.LINGUAGEM,
                },
            )

        self.assertEqual(Tecnologia.objects.count(), 1)
        self.assertEqual(projeto.tecnologias_vinculadas.count(), 1)

    def test_captura_de_tela_pode_ser_anexada_e_aberta(self):
        projeto = self.criar_projeto()
        imagem = SimpleUploadedFile(
            "captura.png",
            b"\x89PNG\r\n\x1a\n" + b"imagem-de-teste",
            content_type="image/png",
        )

        response = self.client.post(
            reverse("projetos:evidencia_criar", args=[projeto.id]),
            {
                "tipo": Evidencia.Tipo.CAPTURA,
                "titulo": "Tela funcionando",
                "descricao": "Registro visual da entrega.",
                "url": "",
                "material": "",
                "imagem": imagem,
                "data": timezone.localdate().isoformat(),
                "validada": "",
            },
        )

        evidencia = Evidencia.objects.get()
        self.assertRedirects(
            response, reverse("projetos:detalhe", args=[projeto.id])
        )
        self.assertTrue(evidencia.imagem.name.endswith(".png"))
        resposta_imagem = self.client.get(
            reverse(
                "projetos:evidencia_imagem",
                args=[projeto.id, evidencia.id],
            )
        )
        self.assertEqual(resposta_imagem.status_code, 200)
        self.assertEqual(resposta_imagem["Cache-Control"], "private, no-store")

    def test_imagem_invalida_e_rejeitada(self):
        projeto = self.criar_projeto()
        arquivo = SimpleUploadedFile(
            "falso.png",
            b"isto nao e uma imagem",
            content_type="image/png",
        )

        response = self.client.post(
            reverse("projetos:evidencia_criar", args=[projeto.id]),
            {
                "tipo": Evidencia.Tipo.CAPTURA,
                "titulo": "Arquivo inválido",
                "descricao": "Teste.",
                "url": "",
                "material": "",
                "imagem": arquivo,
                "data": timezone.localdate().isoformat(),
                "validada": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Envie uma imagem PNG, JPG ou WebP válida")
        self.assertFalse(Evidencia.objects.exists())
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
