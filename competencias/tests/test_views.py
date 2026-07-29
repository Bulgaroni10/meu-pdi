from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from competencias.models import AvaliacaoCompetencia, Competencia
from projetos.models import Evidencia, Projeto
from usuarios.models import Usuario


class CompetenciaViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            nome="Você",
        )
        self.competencia = Competencia.objects.create(
            usuario=self.usuario,
            nome="Microsoft Azure",
            categoria=Competencia.Categoria.TECNICA,
            nivel_desejado=4,
        )

    def criar_evidencia(self, usuario=None):
        usuario = usuario or self.usuario
        projeto = Projeto.objects.create(
            usuario=usuario,
            titulo=f"Projeto de {usuario.nome}",
            data_inicio=timezone.localdate(),
        )
        return Evidencia.objects.create(
            usuario=usuario,
            projeto=projeto,
            tipo=Evidencia.Tipo.RESULTADO,
            titulo="Ambiente publicado",
            descricao="Laboratório executado e validado.",
        )

    def test_lista_abre_sem_login(self):
        response = self.client.get(reverse("competencias:lista"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Soft Skills")
        self.assertContains(response, "Microsoft Azure")

    def test_cria_competencia_para_perfil_pessoal(self):
        response = self.client.post(
            reverse("competencias:criar"),
            {
                "nome": "PowerShell",
                "categoria": Competencia.Categoria.TECNICA,
                "descricao": "Automação de rotinas",
                "nivel_desejado": 4,
                "criterios": "Scripts reutilizáveis e testados",
                "prazo": "",
            },
        )

        criada = Competencia.objects.get(nome="PowerShell")
        self.assertRedirects(
            response, reverse("competencias:detalhe", args=[criada.id])
        )
        self.assertEqual(criada.usuario, self.usuario)

    def test_avaliacao_exige_ao_menos_uma_evidencia(self):
        response = self.client.post(
            reverse("competencias:avaliar", args=[self.competencia.id]),
            {
                "nivel": 2,
                "justificativa": "Conhecimento aplicado.",
                "data": timezone.localdate().isoformat(),
                "evidencias": [],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo é obrigatório")
        self.assertFalse(AvaliacaoCompetencia.objects.exists())

    def test_registra_nivel_com_evidencia_do_proprio_perfil(self):
        evidencia = self.criar_evidencia()

        response = self.client.post(
            reverse("competencias:avaliar", args=[self.competencia.id]),
            {
                "nivel": 3,
                "justificativa": "Implantei um ambiente funcional.",
                "data": timezone.localdate().isoformat(),
                "evidencias": [str(evidencia.id)],
            },
        )

        avaliacao = AvaliacaoCompetencia.objects.get()
        self.assertRedirects(
            response,
            reverse("competencias:detalhe", args=[self.competencia.id]),
        )
        self.assertEqual(avaliacao.nivel, 3)
        self.assertEqual(list(avaliacao.evidencias.all()), [evidencia])

    def test_competencia_de_outro_usuario_retorna_404(self):
        outro = Usuario.objects.create_user(
            email="outro@meupdi.local",
            nome="Outro",
        )
        competencia = Competencia.objects.create(
            usuario=outro,
            nome="Competência alheia",
            categoria=Competencia.Categoria.TECNICA,
        )

        response = self.client.get(
            reverse("competencias:detalhe", args=[competencia.id])
        )

        self.assertEqual(response.status_code, 404)
