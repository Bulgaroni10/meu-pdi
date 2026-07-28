from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from estudos.models import Aula, Curso, Disciplina, Periodo, StatusEstudo, Trilha
from objetivos.models import Objetivo
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Cria a estrutura pessoal de estudos, incluindo a pós-graduação."

    @transaction.atomic
    def handle(self, *args, **options):
        usuario = Usuario.objects.get(pk=1)
        objetivo = Objetivo.objects.filter(usuario=usuario).first()
        trilha, _ = Trilha.objects.get_or_create(
            usuario=usuario,
            titulo="Microsoft Azure",
            defaults={
                "descricao": "Trilha prática para fundamentos e administração do Azure.",
                "categoria": Trilha.Categoria.AZURE,
                "nivel": Trilha.Nivel.INICIANTE,
                "prioridade": "alta",
                "status": StatusEstudo.EM_ANDAMENTO,
                "progresso": 10,
                "carga_horaria_prevista": 80,
                "carga_horaria_realizada": 8,
                "objetivo": objetivo,
            },
        )
        curso, _ = Curso.objects.get_or_create(
            usuario=usuario,
            nome="Preparação AZ-104",
            defaults={
                "instituicao": "Estudo pessoal",
                "tipo": Curso.Tipo.CERTIFICACAO,
                "status": StatusEstudo.EM_ANDAMENTO,
                "carga_horaria": 60,
            },
        )
        curso.trilhas.add(trilha)
        periodo, _ = Periodo.objects.get_or_create(
            usuario=usuario,
            curso=curso,
            numero=1,
            defaults={
                "nome": "Fundamentos e identidade",
                "status": StatusEstudo.EM_ANDAMENTO,
            },
        )
        disciplina, _ = Disciplina.objects.get_or_create(
            usuario=usuario,
            curso=curso,
            periodo=periodo,
            nome="Fundamentos de Azure",
            defaults={
                "status": StatusEstudo.EM_ANDAMENTO,
                "carga_horaria": 12,
                "progresso": 10,
                "ementa": "Cloud, assinaturas, grupos de recursos e identidade.",
            },
        )
        Aula.objects.get_or_create(
            usuario=usuario,
            disciplina=disciplina,
            numero=1,
            defaults={
                "titulo": "Modelos de nuvem e serviços Azure",
                "data": timezone.localdate(),
                "status": StatusEstudo.EM_ANDAMENTO,
                "duracao_prevista": 60,
                "descricao": "IaaS, PaaS, SaaS e modelo de responsabilidade compartilhada.",
                "tags": "azure, cloud, fundamentos",
            },
        )

        pos, _ = Curso.objects.update_or_create(
            usuario=usuario,
            nome="Arquitetura e Projetos de Cloud Computing",
            defaults={
                "instituicao": "Pós-graduação",
                "tipo": Curso.Tipo.POS,
                "descricao": "Formação pessoal em arquitetura e projetos de computação em nuvem.",
                "status": StatusEstudo.EM_ANDAMENTO,
                "carga_horaria": 360,
            },
        )
        periodo_pos, _ = Periodo.objects.update_or_create(
            usuario=usuario,
            curso=pos,
            numero=1,
            defaults={
                "nome": "Disciplinas da pós-graduação",
                "status": StatusEstudo.EM_ANDAMENTO,
            },
        )
        estrutura = {
            "Desenvolvimento Pessoal, Carreira, Empregabilidade": [
                "Autoconhecimento e planejamento de carreira",
                "Competências profissionais e empregabilidade",
                "Comunicação, networking e marca pessoal",
                "Plano de desenvolvimento e próximos passos",
            ],
            "Sistema de Apoio a Decisões - SAD": [
                "Fundamentos de sistemas de apoio à decisão",
                "Dados, informação e modelos decisórios",
                "Business Intelligence e indicadores",
                "Estudo de caso e tomada de decisão",
            ],
            "Fundamentos de Segurança da Informação": [
                "Princípios e pilares da segurança",
                "Riscos, ameaças e vulnerabilidades",
                "Controles de acesso e proteção de dados",
                "Governança, políticas e resposta a incidentes",
            ],
            "Fundamentos e Projeto de Big Data": [
                "Conceitos e arquitetura de Big Data",
                "Coleta, armazenamento e processamento de dados",
                "Ecossistemas e serviços de dados em nuvem",
                "Projeto prático de solução Big Data",
            ],
            "Fundamentos de TI para Cloud Computing": [
                "Infraestrutura, redes e virtualização",
                "Sistemas operacionais e armazenamento",
                "Modelos e serviços de computação em nuvem",
                "Arquitetura básica de uma solução cloud",
            ],
        }
        for nome_disciplina, conteudos in estrutura.items():
            disciplina_pos, _ = Disciplina.objects.update_or_create(
                usuario=usuario,
                curso=pos,
                nome=nome_disciplina,
                defaults={
                    "periodo": periodo_pos,
                    "status": StatusEstudo.EM_ANDAMENTO,
                    "carga_horaria": 24,
                    "ementa": "Disciplina da pós-graduação organizada em quatro conteúdos.",
                },
            )
            for numero, titulo in enumerate(conteudos, start=1):
                Aula.objects.update_or_create(
                    usuario=usuario,
                    disciplina=disciplina_pos,
                    numero=numero,
                    defaults={
                        "titulo": titulo,
                        "data": timezone.localdate(),
                        "status": StatusEstudo.PLANEJADO,
                        "duracao_prevista": 90,
                        "descricao": f"Conteúdo {numero} de {nome_disciplina}.",
                        "tags": "pós-graduação, cloud computing",
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Estudos prontos: pós-graduação com 5 disciplinas e 4 conteúdos em cada."
            )
        )
