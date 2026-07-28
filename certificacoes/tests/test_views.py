from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from certificacoes.models import Certificacao
from usuarios.models import Usuario


class CertificacaoViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            nome="Você",
        )
        self.hoje = timezone.localdate()

    def dados_formulario(self, **kwargs):
        dados = {
            "nome": "Azure Administrator Associate",
            "instituicao": "Microsoft",
            "codigo": "AZ-104",
            "status": Certificacao.Status.PREPARANDO,
            "prioridade": Certificacao.Prioridade.ALTA,
            "progresso": 25,
            "data_inicio": self.hoje.isoformat(),
            "data_prova": (self.hoje + timedelta(days=90)).isoformat(),
            "data_resultado": "",
            "data_validade": "",
            "custo_previsto": "600.00",
            "custo_real": "",
            "nota": "",
            "objetivo": "",
            "trilha": "",
            "certificado": "",
            "url_oficial": "https://learn.microsoft.com/",
            "url_agendamento": "",
            "observacoes": "Revisar identidade, rede e governança.",
        }
        dados.update(kwargs)
        return dados

    def test_lista_abre_sem_login(self):
        response = self.client.get(reverse("certificacoes:lista"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Minhas certificações")

    def test_cria_certificacao_para_perfil_pessoal(self):
        response = self.client.post(
            reverse("certificacoes:criar"), self.dados_formulario()
        )

        certificacao = Certificacao.objects.get()
        self.assertRedirects(
            response,
            reverse("certificacoes:detalhe", args=[certificacao.id]),
        )
        self.assertEqual(certificacao.usuario, self.usuario)
        self.assertEqual(certificacao.codigo, "AZ-104")

    def test_recusa_prova_anterior_ao_inicio(self):
        response = self.client.post(
            reverse("certificacoes:criar"),
            self.dados_formulario(
                data_prova=(self.hoje - timedelta(days=1)).isoformat()
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "não pode ser anterior")
        self.assertFalse(Certificacao.objects.exists())

    def test_aprovacao_define_progresso_total(self):
        response = self.client.post(
            reverse("certificacoes:criar"),
            self.dados_formulario(
                status=Certificacao.Status.APROVADA,
                progresso=80,
                data_prova=self.hoje.isoformat(),
                data_resultado=self.hoje.isoformat(),
                nota="850.00",
            ),
        )

        certificacao = Certificacao.objects.get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(certificacao.progresso, 100)
        self.assertEqual(certificacao.status, Certificacao.Status.APROVADA)

    def test_certificacao_de_outro_usuario_retorna_404(self):
        outro = Usuario.objects.create_user(
            email="outro@meupdi.local",
            nome="Outro",
        )
        certificacao = Certificacao.objects.create(
            usuario=outro,
            nome="Certificação alheia",
            instituicao="Instituição",
            data_inicio=self.hoje,
        )

        response = self.client.get(
            reverse("certificacoes:detalhe", args=[certificacao.id])
        )

        self.assertEqual(response.status_code, 404)
