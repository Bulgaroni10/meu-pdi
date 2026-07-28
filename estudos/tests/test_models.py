from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from estudos.models import Curso, Disciplina, StatusEstudo, Trilha
from usuarios.models import Usuario


class EstudosModelTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1, email="pessoal@meupdi.local", nome="Você"
        )

    def test_disciplina_recusa_curso_de_outro_perfil(self):
        outro = Usuario.objects.create_user(email="outro@example.com", nome="Outro")
        curso = Curso.objects.create(
            usuario=outro, nome="Curso alheio", tipo=Curso.Tipo.LIVRE
        )
        disciplina = Disciplina(
            usuario=self.usuario,
            curso=curso,
            nome="Disciplina inválida",
        )

        with self.assertRaises(ValidationError):
            disciplina.full_clean()

    def test_trilha_valida_progresso(self):
        trilha = Trilha(
            usuario=self.usuario,
            titulo="Azure",
            categoria=Trilha.Categoria.AZURE,
            progresso=101,
            data_inicio=timezone.localdate(),
        )

        with self.assertRaises(ValidationError):
            trilha.full_clean()
