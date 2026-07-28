from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from objetivos.models import Objetivo
from roadmap.models import FaseRoadmap, Roadmap
from usuarios.models import Usuario


class RoadmapModelTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            nome="Você",
        )

    def test_progresso_e_calculado_pelas_fases(self):
        roadmap = Roadmap.objects.create(
            usuario=self.usuario,
            nome="Roadmap Azure",
        )
        FaseRoadmap.objects.create(
            usuario=self.usuario,
            roadmap=roadmap,
            titulo="Fundamentos",
            ordem=1,
            progresso=20,
        )
        FaseRoadmap.objects.create(
            usuario=self.usuario,
            roadmap=roadmap,
            titulo="Redes",
            ordem=2,
            progresso=60,
        )

        self.assertEqual(roadmap.progresso, 40)

    def test_objetivo_de_outro_perfil_e_recusado(self):
        outro = Usuario.objects.create_user(
            email="outro@meupdi.local",
            nome="Outro",
        )
        objetivo = Objetivo.objects.create(
            usuario=outro,
            titulo="Objetivo alheio",
            data_inicio=timezone.localdate(),
        )
        roadmap = Roadmap(
            usuario=self.usuario,
            nome="Roadmap inválido",
            objetivo=objetivo,
        )

        with self.assertRaises(ValidationError):
            roadmap.full_clean()
