from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from revisoes.models import AcaoRevisao, RevisaoPeriodica
from usuarios.models import Usuario


class RevisaoViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            nome="Você",
        )
        self.hoje = timezone.localdate()

    def criar_revisao(self, **kwargs):
        dados = {
            "usuario": self.usuario,
            "titulo": "Revisão da semana",
            "tipo": RevisaoPeriodica.Tipo.SEMANAL,
            "periodo_inicio": self.hoje - timedelta(days=6),
            "periodo_fim": self.hoje,
        }
        dados.update(kwargs)
        return RevisaoPeriodica.objects.create(**dados)

    def dados_formulario(self, **kwargs):
        dados = {
            "titulo": "Fechamento mensal",
            "tipo": RevisaoPeriodica.Tipo.MENSAL,
            "periodo_inicio": (self.hoje - timedelta(days=20)).isoformat(),
            "periodo_fim": self.hoje.isoformat(),
            "nota_periodo": 4,
            "conquistas": "Concluí uma entrega prática.",
            "dificuldades": "Organização do tempo.",
            "aprendizados": "Planejar blocos menores.",
            "ajustes": "Reservar três sessões semanais.",
            "conclusao": "O mês teve avanço consistente.",
        }
        dados.update(kwargs)
        return dados

    def test_lista_abre_sem_login(self):
        response = self.client.get(reverse("revisoes:lista"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Revisões periódicas")

    def test_cria_revisao_para_perfil_pessoal(self):
        response = self.client.post(
            reverse("revisoes:criar"), self.dados_formulario()
        )

        revisao = RevisaoPeriodica.objects.get()
        self.assertRedirects(
            response, reverse("revisoes:detalhe", args=[revisao.id])
        )
        self.assertEqual(revisao.usuario, self.usuario)
        self.assertEqual(revisao.status, RevisaoPeriodica.Status.RASCUNHO)

    def test_recusa_periodo_com_datas_invertidas(self):
        response = self.client.post(
            reverse("revisoes:criar"),
            self.dados_formulario(
                periodo_inicio=self.hoje.isoformat(),
                periodo_fim=(self.hoje - timedelta(days=1)).isoformat(),
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "não pode ser anterior")
        self.assertFalse(RevisaoPeriodica.objects.exists())

    def test_adiciona_e_conclui_proxima_acao(self):
        revisao = self.criar_revisao()
        response = self.client.post(
            reverse("revisoes:acao_criar", args=[revisao.id]),
            {
                "descricao": "Concluir documentação",
                "prazo": self.hoje.isoformat(),
                "status": AcaoRevisao.Status.PENDENTE,
                "objetivo": "",
                "projeto": "",
                "competencia": "",
            },
        )
        acao = AcaoRevisao.objects.get()
        self.assertRedirects(
            response, reverse("revisoes:detalhe", args=[revisao.id])
        )

        self.client.post(
            reverse("revisoes:acao_alternar", args=[revisao.id, acao.id])
        )

        acao.refresh_from_db()
        self.assertEqual(acao.status, AcaoRevisao.Status.CONCLUIDA)

    def test_concluir_revisao_registra_data(self):
        revisao = self.criar_revisao()

        self.client.post(reverse("revisoes:concluir", args=[revisao.id]))

        revisao.refresh_from_db()
        self.assertEqual(revisao.status, RevisaoPeriodica.Status.CONCLUIDA)
        self.assertIsNotNone(revisao.concluida_em)

    def test_revisao_de_outro_usuario_retorna_404(self):
        outro = Usuario.objects.create_user(
            email="outro@meupdi.local",
            nome="Outro",
        )
        revisao = RevisaoPeriodica.objects.create(
            usuario=outro,
            titulo="Revisão alheia",
            tipo=RevisaoPeriodica.Tipo.MENSAL,
            periodo_inicio=self.hoje,
            periodo_fim=self.hoje,
        )

        response = self.client.get(
            reverse("revisoes:detalhe", args=[revisao.id])
        )

        self.assertEqual(response.status_code, 404)
