from django.test import TestCase
from django.utils import timezone

from objetivos.forms import ObjetivoForm
from objetivos.models import HistoricoObjetivo, Tag
from objetivos.services import atualizar_objetivo, criar_objetivo
from usuarios.models import Usuario


class ObjetivoServiceTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            id=1,
            email="pessoal@meupdi.local",
            nome="Você",
        )

    def dados(self, **kwargs):
        dados = {
            "titulo": "Aprender Azure",
            "descricao": "Construir uma base prática.",
            "categoria": "profissional",
            "motivo": "Evolução de carreira",
            "data_inicio": timezone.localdate().isoformat(),
            "prazo": "",
            "prioridade": "alta",
            "status": "em_andamento",
            "progresso": 20,
            "resultado_esperado": "Administrar recursos",
            "evidencia_esperada": "Laboratório documentado",
            "proxima_acao": "Concluir módulo de identidade",
            "obstaculos": "",
            "observacoes": "",
            "tags_texto": "Azure, Cloud, azure",
        }
        dados.update(kwargs)
        return dados

    def test_criacao_define_proprietario_tags_e_historico(self):
        form = ObjetivoForm(self.dados())
        self.assertTrue(form.is_valid(), form.errors)

        objetivo = criar_objetivo(form, self.usuario)

        self.assertEqual(objetivo.usuario, self.usuario)
        self.assertEqual(Tag.objects.count(), 2)
        self.assertEqual(objetivo.tags.count(), 2)
        self.assertTrue(
            objetivo.historico.filter(
                tipo=HistoricoObjetivo.Tipo.CRIACAO
            ).exists()
        )

    def test_edicao_registra_campos_alterados(self):
        form = ObjetivoForm(self.dados())
        self.assertTrue(form.is_valid(), form.errors)
        objetivo = criar_objetivo(form, self.usuario)
        form_edicao = ObjetivoForm(
            self.dados(progresso=55, proxima_acao="Criar uma VM"),
            instance=objetivo,
        )
        self.assertTrue(form_edicao.is_valid(), form_edicao.errors)

        atualizar_objetivo(form_edicao, self.usuario)

        self.assertTrue(
            objetivo.historico.filter(campo="progresso").exists()
        )
        self.assertTrue(
            objetivo.historico.filter(campo="proxima_acao").exists()
        )
