from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from objetivos.models import Objetivo
from usuarios.models import Usuario


class ObjetivoModelTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            nome="Você",
        )

    def objetivo(self, **kwargs):
        dados = {
            "usuario": self.usuario,
            "titulo": "Evoluir profissionalmente",
            "data_inicio": timezone.localdate(),
        }
        dados.update(kwargs)
        return Objetivo(**dados)

    def test_progresso_deve_ficar_entre_zero_e_cem(self):
        objetivo = self.objetivo(progresso=101)

        with self.assertRaises(ValidationError):
            objetivo.full_clean()

    def test_prazo_nao_pode_ser_anterior_ao_inicio(self):
        objetivo = self.objetivo(
            prazo=timezone.localdate() - timedelta(days=1)
        )

        with self.assertRaisesMessage(
            ValidationError, "O prazo não pode ser anterior à data de início."
        ):
            objetivo.full_clean()

    def test_atraso_e_calculado_automaticamente(self):
        objetivo = self.objetivo(
            data_inicio=timezone.localdate() - timedelta(days=10),
            prazo=timezone.localdate() - timedelta(days=1),
            status=Objetivo.Status.EM_ANDAMENTO,
        )
        objetivo.save()

        self.assertTrue(objetivo.is_atrasado)
        self.assertEqual(objetivo.status_efetivo, Objetivo.Status.ATRASADO)

    def test_conclusao_registra_data_e_cem_por_cento(self):
        objetivo = self.objetivo(
            status=Objetivo.Status.CONCLUIDO,
            progresso=40,
        )
        objetivo.save()

        self.assertEqual(objetivo.progresso, 100)
        self.assertEqual(objetivo.data_conclusao, timezone.localdate())
