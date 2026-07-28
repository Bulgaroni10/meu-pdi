from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from estudos.models import Aula, Curso, Disciplina, SessaoEstudo, StatusEstudo, Trilha
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

    def test_registra_tempo_do_cronometro(self):
        response = self.client.post(
            reverse("estudos:registrar_sessao"),
            {"duracao_segundos": 5_400},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        sessao = SessaoEstudo.objects.get()
        self.assertEqual(sessao.usuario, self.usuario)
        self.assertEqual(sessao.duracao_segundos, 5_400)
        self.assertEqual(
            round((sessao.encerrada_em - sessao.iniciada_em).total_seconds()),
            5_400,
        )

    def test_rejeita_tempo_invalido_do_cronometro(self):
        response = self.client.post(
            reverse("estudos:registrar_sessao"),
            {"duracao_segundos": 0},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        self.assertFalse(SessaoEstudo.objects.exists())

    def test_alterna_conclusao_de_trilha_curso_disciplina_e_aula(self):
        trilha = Trilha.objects.create(
            usuario=self.usuario,
            titulo="Cloud",
            categoria=Trilha.Categoria.AZURE,
        )
        curso = Curso.objects.create(
            usuario=self.usuario,
            nome="Fundamentos",
            tipo=Curso.Tipo.LIVRE,
        )
        disciplina = Disciplina.objects.create(
            usuario=self.usuario,
            curso=curso,
            nome="Infraestrutura",
        )
        aula = Aula.objects.create(
            usuario=self.usuario,
            disciplina=disciplina,
            titulo="Redes",
        )

        for tipo, item in (
            ("trilha", trilha),
            ("curso", curso),
            ("disciplina", disciplina),
            ("aula", aula),
        ):
            response = self.client.post(
                reverse("estudos:alternar_conclusao", args=[tipo, item.id])
            )
            self.assertEqual(response.status_code, 302)
            item.refresh_from_db()
            self.assertEqual(item.status, StatusEstudo.CONCLUIDO)

        self.assertEqual(trilha.progresso, 100)
        self.assertEqual(disciplina.progresso, 100)
        self.assertTrue(aula.concluida)
        self.assertEqual(curso.data_real_conclusao, timezone.localdate())

        self.client.post(
            reverse("estudos:alternar_conclusao", args=["aula", aula.id])
        )
        aula.refresh_from_db()
        self.assertEqual(aula.status, StatusEstudo.PLANEJADO)
        self.assertFalse(aula.concluida)

    def test_nao_altera_item_de_outro_perfil(self):
        outro = Usuario.objects.create_user(email="outro2@example.com", nome="Outro")
        trilha = Trilha.objects.create(
            usuario=outro,
            titulo="Privada",
            categoria=Trilha.Categoria.OUTRO,
        )

        response = self.client.post(
            reverse("estudos:alternar_conclusao", args=["trilha", trilha.id])
        )

        self.assertEqual(response.status_code, 404)
        trilha.refresh_from_db()
        self.assertEqual(trilha.status, StatusEstudo.PLANEJADO)
