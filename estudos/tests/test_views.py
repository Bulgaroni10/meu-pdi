from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from estudos.models import Aula, Curso, Disciplina, Trilha
from usuarios.models import Usuario


class EstudosViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1, email="pessoal@meupdi.local", nome="Você"
        )

    def test_central_abre_direto(self):
        response = self.client.get(reverse("estudos:inicio"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Central de estudos")

    def test_cria_trilha_para_perfil_pessoal(self):
        response = self.client.post(
            reverse("estudos:trilha_criar"),
            {
                "titulo": "Microsoft Azure",
                "descricao": "Do básico à administração.",
                "categoria": "azure",
                "nivel": "iniciante",
                "prioridade": "alta",
                "data_inicio": timezone.localdate().isoformat(),
                "prazo": "",
                "status": "em_andamento",
                "progresso": 10,
                "carga_horaria_prevista": "80",
                "carga_horaria_realizada": "8",
                "prerequisitos": "",
                "objetivo": "",
                "observacoes": "",
            },
        )

        self.assertRedirects(response, reverse("estudos:trilhas"))
        self.assertEqual(Trilha.objects.get().usuario, self.usuario)

    def test_cria_curso_disciplina_e_aula(self):
        curso = Curso.objects.create(
            usuario=self.usuario,
            nome="AZ-104",
            tipo=Curso.Tipo.CERTIFICACAO,
        )
        disciplina = Disciplina.objects.create(
            usuario=self.usuario,
            curso=curso,
            nome="Identidade",
        )
        response = self.client.post(
            reverse("estudos:aula_criar"),
            {
                "disciplina": str(disciplina.id),
                "titulo": "Microsoft Entra ID",
                "numero": 1,
                "data": timezone.localdate().isoformat(),
                "professor": "",
                "descricao": "Usuários, grupos e funções.",
                "status": "em_andamento",
                "duracao_prevista": 60,
                "duracao_estudada": 30,
                "dificuldade": "media",
                "resumo": "",
                "duvidas": "",
                "aplicacao_pratica": "",
                "proxima_revisao": "",
                "concluida": "",
                "favorita": "",
                "tags": "azure, identidade",
            },
        )

        self.assertRedirects(response, reverse("estudos:aulas"))
        self.assertEqual(Aula.objects.get().disciplina, disciplina)

    def test_curso_de_outro_perfil_retorna_404(self):
        outro = Usuario.objects.create_user(email="outro@example.com", nome="Outro")
        curso = Curso.objects.create(
            usuario=outro,
            nome="Privado",
            tipo=Curso.Tipo.LIVRE,
        )

        response = self.client.get(
            reverse("estudos:curso_detalhe", args=[curso.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_disciplina_exibe_os_conteudos_do_curso(self):
        curso = Curso.objects.create(
            usuario=self.usuario,
            nome="Pós em Cloud",
            tipo=Curso.Tipo.POS,
        )
        disciplina = Disciplina.objects.create(
            usuario=self.usuario,
            curso=curso,
            nome="Segurança da Informação",
        )
        for numero in range(1, 5):
            Aula.objects.create(
                usuario=self.usuario,
                disciplina=disciplina,
                numero=numero,
                titulo=f"Conteúdo {numero}",
            )

        response = self.client.get(
            reverse("estudos:disciplina_detalhe", args=[disciplina.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pós em Cloud")
        self.assertContains(response, "Conteúdo 4")

    def test_exclusao_de_conteudo_exige_post(self):
        curso = Curso.objects.create(
            usuario=self.usuario,
            nome="Pós em Cloud",
            tipo=Curso.Tipo.POS,
        )
        disciplina = Disciplina.objects.create(
            usuario=self.usuario,
            curso=curso,
            nome="Cloud",
        )
        aula = Aula.objects.create(
            usuario=self.usuario,
            disciplina=disciplina,
            titulo="Conteúdo removível",
        )

        response = self.client.get(
            reverse("estudos:excluir", args=["aula", aula.id])
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Aula.objects.filter(id=aula.id).exists())
