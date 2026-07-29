from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from objetivos.models import HistoricoObjetivo, Objetivo
from usuarios.models import Usuario


class ObjetivoViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            nome="Você",
        )

    def dados_formulario(self, **kwargs):
        dados = {
            "titulo": "Chegar ao nível pleno",
            "descricao": "Evolução profissional baseada em prática.",
            "categoria": Objetivo.Categoria.PROFISSIONAL,
            "motivo": "Ampliar impacto e autonomia",
            "data_inicio": timezone.localdate().isoformat(),
            "prazo": "",
            "prioridade": Objetivo.Prioridade.ALTA,
            "status": Objetivo.Status.EM_ANDAMENTO,
            "progresso": 15,
            "resultado_esperado": "Atuar com autonomia",
            "evidencia_esperada": "Projetos documentados",
            "proxima_acao": "Mapear lacunas técnicas",
            "obstaculos": "",
            "observacoes": "",
            "tags_texto": "carreira, infraestrutura",
        }
        dados.update(kwargs)
        return dados

    def criar_objetivo(self, **kwargs):
        dados = {
            "usuario": self.usuario,
            "titulo": "Objetivo de teste",
            "data_inicio": timezone.localdate(),
            "status": Objetivo.Status.EM_ANDAMENTO,
        }
        dados.update(kwargs)
        return Objetivo.objects.create(**dados)

    def test_lista_abre_direto(self):
        response = self.client.get(reverse("objetivos:lista"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Metas com Prazos")

    def test_formulario_de_criacao_renderiza(self):
        response = self.client.get(reverse("objetivos:criar"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Novo objetivo")
        self.assertContains(response, "Evidência de sucesso")

    def test_cria_objetivo_para_perfil_pessoal(self):
        response = self.client.post(
            reverse("objetivos:criar"),
            self.dados_formulario(),
        )

        objetivo = Objetivo.objects.get()
        self.assertRedirects(
            response,
            reverse("objetivos:detalhe", args=[objetivo.id]),
        )
        self.assertEqual(objetivo.usuario, self.usuario)
        self.assertEqual(objetivo.tags.count(), 2)
        self.assertTrue(
            objetivo.historico.filter(
                tipo=HistoricoObjetivo.Tipo.CRIACAO
            ).exists()
        )

    def test_filtro_de_atrasados(self):
        atrasado = self.criar_objetivo(
            titulo="Meta vencida",
            data_inicio=timezone.localdate() - timedelta(days=5),
            prazo=timezone.localdate() - timedelta(days=1),
        )
        self.criar_objetivo(titulo="Meta no prazo")

        response = self.client.get(
            reverse("objetivos:lista"),
            {"status": Objetivo.Status.ATRASADO},
        )

        self.assertContains(response, atrasado.titulo)
        self.assertNotContains(response, "Meta no prazo")

    def test_objetivo_de_outro_usuario_retorna_404(self):
        outro = Usuario.objects.create_user(
            email="outro@meupdi.local",
            nome="Outro",
        )
        objetivo = Objetivo.objects.create(
            usuario=outro,
            titulo="Objetivo alheio",
            data_inicio=timezone.localdate(),
        )

        response = self.client.get(
            reverse("objetivos:detalhe", args=[objetivo.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_arquivamento_preserva_objetivo_e_registra_historico(self):
        objetivo = self.criar_objetivo()

        response = self.client.post(
            reverse("objetivos:arquivar", args=[objetivo.id])
        )

        self.assertRedirects(response, reverse("objetivos:lista"))
        objetivo.refresh_from_db()
        self.assertIsNotNone(objetivo.arquivado_em)
        self.assertTrue(
            objetivo.historico.filter(
                tipo=HistoricoObjetivo.Tipo.ARQUIVAMENTO
            ).exists()
        )

    def test_resposta_htmx_retorna_apenas_resultados(self):
        self.criar_objetivo()

        response = self.client.get(
            reverse("objetivos:lista"),
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "objetivos/_lista_resultados.html")
        self.assertNotContains(response, "<html")
