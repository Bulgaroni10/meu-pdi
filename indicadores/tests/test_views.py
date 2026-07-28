from django.test import TestCase
from django.urls import reverse
from datetime import timedelta

from django.utils import timezone

from estudos.models import SessaoEstudo
from objetivos.models import Objetivo
from usuarios.models import Usuario


class IndicadoresViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            nome="Você",
        )

    def test_painel_abre_com_estado_vazio(self):
        response = self.client.get(reverse("indicadores:painel"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Indicadores do PDI")
        self.assertEqual(response.context["progresso"]["valor"], 0)
        self.assertEqual(len(response.context["meses_estudo"]), 6)

    def test_indicadores_usam_somente_dados_do_perfil_pessoal(self):
        Objetivo.objects.create(
            usuario=self.usuario,
            titulo="Objetivo próprio",
            data_inicio=timezone.localdate(),
            status=Objetivo.Status.EM_ANDAMENTO,
            progresso=40,
        )
        outro = Usuario.objects.create_user(
            email="outro@meupdi.local",
            nome="Outro",
        )
        Objetivo.objects.create(
            usuario=outro,
            titulo="Objetivo alheio",
            data_inicio=timezone.localdate(),
            status=Objetivo.Status.EM_ANDAMENTO,
            progresso=100,
        )

        response = self.client.get(reverse("indicadores:painel"))

        andamento = next(
            item
            for item in response.context["objetivos_status"]
            if item["nome"] == "Em andamento"
        )
        self.assertEqual(andamento["valor"], 1)
        self.assertEqual(response.context["progresso"]["valor"], 40)
        self.assertEqual(response.context["progresso"]["cobertura"], 25)

    def test_relatorio_executivo_pode_ser_apresentado(self):
        response = self.client.get(reverse("indicadores:relatorio"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Relatório executivo do PDI")
        self.assertContains(response, "Imprimir ou salvar em PDF")

    def test_cronometro_entra_nos_indicadores_de_horas(self):
        agora = timezone.now()
        SessaoEstudo.objects.create(
            usuario=self.usuario,
            iniciada_em=agora - timedelta(hours=2),
            encerrada_em=agora,
            duracao_segundos=7_200,
        )

        response = self.client.get(reverse("indicadores:painel"))

        horas = next(
            item for item in response.context["kpis"]
            if item["rotulo"] == "Horas registradas"
        )
        self.assertEqual(horas["valor"], "2h")
        self.assertEqual(response.context["meses_estudo"][-1]["horas"], 2)
