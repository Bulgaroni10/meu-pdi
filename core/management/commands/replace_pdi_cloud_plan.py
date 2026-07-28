from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from anotacoes.models import Anotacao
from biblioteca.models import MaterialPDF
from certificacoes.models import Certificacao
from competencias.models import (
    AvaliacaoCompetencia,
    Competencia,
    EvidenciaCompetencia,
)
from estudos.models import Aula, Curso, Disciplina, Periodo, StatusEstudo, Trilha
from objetivos.models import Objetivo, Tag
from projetos.models import (
    Evidencia,
    MarcoProjeto,
    Projeto,
    ProjetoTecnologia,
    TarefaProjeto,
    Tecnologia,
)
from revisoes.models import AcaoRevisao, RevisaoPeriodica
from roadmap.models import (
    EntregaRoadmap,
    EtapaRoadmap,
    FaseRoadmap,
    FonteRoadmap,
    Roadmap,
)
from usuarios.models import Usuario


PLAN_MARKER = "seed:pdi-infra-cloud-gratuito-v1"
PLAN_START = date(2026, 8, 3)

WEEKS = [
    ("Fundamentos de Redes", "IPv4, máscara, gateway e exercícios de subnetting", "Topologia hospitalar simulada no Packet Tracer", "Demonstra base de redes e capacidade de diagnóstico."),
    ("Fundamentos de Redes", "DNS, DHCP, NAT, portas TCP/UDP e comandos de diagnóstico", "Topologia hospitalar simulada no Packet Tracer", "Demonstra base de redes e capacidade de diagnóstico."),
    ("Fundamentos de Redes", "VLAN, roteamento, firewall e desenho de topologia", "Topologia hospitalar simulada no Packet Tracer", "Demonstra base de redes e capacidade de diagnóstico."),
    ("Fundamentos de Redes", "Montar e documentar a rede hospitalar no Packet Tracer", "Topologia hospitalar simulada no Packet Tracer", "Demonstra base de redes e capacidade de diagnóstico."),
    ("Windows Server e Active Directory", "Instalar Windows Server e promover controlador de domínio", "Hospital Bulgaroni Lab com AD, GPO e pastas por setor", "Prova administração de ambiente corporativo Windows."),
    ("Windows Server e Active Directory", "Criar OUs, usuários, grupos e ingressar estações no domínio", "Hospital Bulgaroni Lab com AD, GPO e pastas por setor", "Prova administração de ambiente corporativo Windows."),
    ("Windows Server e Active Directory", "Configurar DNS, DHCP, GPO e mapeamento de unidades", "Hospital Bulgaroni Lab com AD, GPO e pastas por setor", "Prova administração de ambiente corporativo Windows."),
    ("Windows Server e Active Directory", "Aplicar permissões NTFS/compartilhamento e documentar testes", "Hospital Bulgaroni Lab com AD, GPO e pastas por setor", "Prova administração de ambiente corporativo Windows."),
    ("PowerShell para Infraestrutura", "Cmdlets, ajuda, pipeline, objetos e filtros", "Kit de automação de usuários, auditoria e inventário", "Mostra automação, padronização e redução de erro manual."),
    ("PowerShell para Infraestrutura", "Variáveis, arrays, CSV, loops, condições e funções", "Kit de automação de usuários, auditoria e inventário", "Mostra automação, padronização e redução de erro manual."),
    ("PowerShell para Infraestrutura", "Automatizar criação de usuários e associação a grupos", "Kit de automação de usuários, auditoria e inventário", "Mostra automação, padronização e redução de erro manual."),
    ("PowerShell para Infraestrutura", "Criar auditoria de AD, inventário e logs com tratamento de erros", "Kit de automação de usuários, auditoria e inventário", "Mostra automação, padronização e redução de erro manual."),
    ("Git e GitHub", "Criar repositórios, commits, branches e README", "Publicação profissional dos projetos anteriores", "Cria portfólio verificável e melhora colaboração técnica."),
    ("Git e GitHub", "Usar issues, pull requests e organizar o portfólio", "Publicação profissional dos projetos anteriores", "Cria portfólio verificável e melhora colaboração técnica."),
    ("Azure - Identidade e Governança", "Criar estrutura de assinatura, resource groups e tags", "Governança Azure de empresa fictícia", "Adiciona identidade, segurança e governança cloud."),
    ("Azure - Identidade e Governança", "Estudar Entra ID, usuários, grupos e RBAC", "Governança Azure de empresa fictícia", "Adiciona identidade, segurança e governança cloud."),
    ("Azure - Identidade e Governança", "Aplicar locks, Azure Policy e padrões de nomenclatura", "Governança Azure de empresa fictícia", "Adiciona identidade, segurança e governança cloud."),
    ("Azure - Identidade e Governança", "Criar orçamento, alertas de custo e documentar governança", "Governança Azure de empresa fictícia", "Adiciona identidade, segurança e governança cloud."),
    ("Azure - Redes, Compute e Storage", "Planejar VNet, CIDR e sub-redes", "Hospital híbrido Azure segmentado", "Comprova experiência prática em infraestrutura Azure."),
    ("Azure - Redes, Compute e Storage", "Criar NSGs, regras mínimas e testar conectividade", "Hospital híbrido Azure segmentado", "Comprova experiência prática em infraestrutura Azure."),
    ("Azure - Redes, Compute e Storage", "Implantar VM Windows e VM Linux com acesso seguro", "Hospital híbrido Azure segmentado", "Comprova experiência prática em infraestrutura Azure."),
    ("Azure - Redes, Compute e Storage", "Configurar discos, Storage Account, Blob e Azure Files", "Hospital híbrido Azure segmentado", "Comprova experiência prática em infraestrutura Azure."),
    ("Azure - Redes, Compute e Storage", "Integrar recursos e documentar arquitetura e testes", "Hospital híbrido Azure segmentado", "Comprova experiência prática em infraestrutura Azure."),
    ("Azure - Monitoramento, Backup e Custos", "Configurar Azure Monitor e Log Analytics", "Monitoramento e recuperação do laboratório Azure", "Demonstra operação, disponibilidade e responsabilidade financeira."),
    ("Azure - Monitoramento, Backup e Custos", "Criar alertas de CPU, disponibilidade e espaço", "Monitoramento e recuperação do laboratório Azure", "Demonstra operação, disponibilidade e responsabilidade financeira."),
    ("Azure - Monitoramento, Backup e Custos", "Configurar backup e executar teste de restauração", "Monitoramento e recuperação do laboratório Azure", "Demonstra operação, disponibilidade e responsabilidade financeira."),
    ("Azure - Monitoramento, Backup e Custos", "Revisar custos, destruir recursos e fechar documentação AZ-104", "Monitoramento e recuperação do laboratório Azure", "Demonstra operação, disponibilidade e responsabilidade financeira."),
    ("Terraform", "Instalar Terraform e aprender init, fmt, validate e plan", "Recriar o laboratório Azure por código", "Move o perfil de administrador manual para Cloud/DevOps."),
    ("Terraform", "Criar resource group, VNet, sub-redes e NSGs", "Recriar o laboratório Azure por código", "Move o perfil de administrador manual para Cloud/DevOps."),
    ("Terraform", "Adicionar VM, storage, variables e outputs", "Recriar o laboratório Azure por código", "Move o perfil de administrador manual para Cloud/DevOps."),
    ("Terraform", "Executar apply/destroy, organizar módulos e documentar", "Recriar o laboratório Azure por código", "Move o perfil de administrador manual para Cloud/DevOps."),
    ("Linux para Cloud", "Sistema de arquivos, usuários, grupos e permissões", "Servidor Linux documentado e automatizado", "Fortalece requisito básico de Cloud e DevOps."),
    ("Linux para Cloud", "Processos, systemd, logs e troubleshooting", "Servidor Linux documentado e automatizado", "Fortalece requisito básico de Cloud e DevOps."),
    ("Linux para Cloud", "SSH, rede, firewall, discos e pacotes", "Servidor Linux documentado e automatizado", "Fortalece requisito básico de Cloud e DevOps."),
    ("Linux para Cloud", "Bash, cron, script de diagnóstico e documentação", "Servidor Linux documentado e automatizado", "Fortalece requisito básico de Cloud e DevOps."),
    ("Docker e Docker Compose", "Containers, imagens, comandos e Dockerfile", "Containerizar versão sanitizada da intranet Django", "Conecta desenvolvimento, infraestrutura e portabilidade."),
    ("Docker e Docker Compose", "Volumes, redes, variáveis e logs", "Containerizar versão sanitizada da intranet Django", "Conecta desenvolvimento, infraestrutura e portabilidade."),
    ("Docker e Docker Compose", "Docker Compose com Django e PostgreSQL", "Containerizar versão sanitizada da intranet Django", "Conecta desenvolvimento, infraestrutura e portabilidade."),
    ("Docker e Docker Compose", "Adicionar Nginx/healthcheck, backup e documentação", "Containerizar versão sanitizada da intranet Django", "Conecta desenvolvimento, infraestrutura e portabilidade."),
    ("GitHub Actions e CI/CD", "Workflows, eventos, jobs, runners e secrets", "Pipeline automático da intranet", "Demonstra automação de entrega e práticas DevOps."),
    ("GitHub Actions e CI/CD", "Pipeline de lint e testes", "Pipeline automático da intranet", "Demonstra automação de entrega e práticas DevOps."),
    ("GitHub Actions e CI/CD", "Build e publicação de imagem Docker", "Pipeline automático da intranet", "Demonstra automação de entrega e práticas DevOps."),
    ("GitHub Actions e CI/CD", "Entrega automatizada e documentação do fluxo", "Pipeline automático da intranet", "Demonstra automação de entrega e práticas DevOps."),
    ("Projeto Integrado e Empregabilidade", "Definir arquitetura final e requisitos", "Plataforma hospitalar híbrida automatizada", "Gera caso completo para vagas de Infra Pleno, Cloud Jr e DevOps Jr."),
    ("Projeto Integrado e Empregabilidade", "Integrar AD, PowerShell, Azure e Terraform", "Plataforma hospitalar híbrida automatizada", "Gera caso completo para vagas de Infra Pleno, Cloud Jr e DevOps Jr."),
    ("Projeto Integrado e Empregabilidade", "Integrar Docker, monitoramento e CI/CD", "Plataforma hospitalar híbrida automatizada", "Gera caso completo para vagas de Infra Pleno, Cloud Jr e DevOps Jr."),
    ("Projeto Integrado e Empregabilidade", "Produzir diagramas, README, demonstração e estudo de caso", "Plataforma hospitalar híbrida automatizada", "Gera caso completo para vagas de Infra Pleno, Cloud Jr e DevOps Jr."),
    ("Projeto Integrado e Empregabilidade", "Atualizar currículo/LinkedIn e simular entrevista técnica", "Plataforma hospitalar híbrida automatizada", "Gera caso completo para vagas de Infra Pleno, Cloud Jr e DevOps Jr."),
]

RESOURCES = {
    "Fundamentos de Redes": [
        ("Networking Basics", "Cisco Skills for All", "https://skillsforall.com/course/networking-basics?courseLang=en-US"),
        ("Networking Essentials", "Cisco Skills for All", "https://skillsforall.com/course/networking-essentials"),
        ("Getting Started with Cisco Packet Tracer", "Cisco Skills for All", "https://skillsforall.com/course/getting-started-cisco-packet-tracer"),
    ],
    "Windows Server e Active Directory": [
        ("Active Directory Domain Services", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/paths/active-directory-domain-services/"),
        ("Administer Active Directory Domain Services", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/paths/administer-active-directory-domain-services/"),
    ],
    "PowerShell para Infraestrutura": [
        ("Get started with Windows PowerShell", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/paths/get-started-windows-powershell/"),
        ("Maintain system administration tasks", "Microsoft Learn", "https://learn.microsoft.com/pt-br/training/paths/maintain-system-administration-tasks-windows-powershell/"),
        ("Gerenciar AD DS usando cmdlets", "Microsoft Learn", "https://learn.microsoft.com/pt-br/training/modules/manage-active-directory-domain-services-use-powershell-cmdlets/"),
    ],
    "Git e GitHub": [
        ("GitHub Skills", "GitHub", "https://skills.github.com/"),
    ],
    "Azure - Identidade e Governança": [
        ("AZ-104: Prerequisites", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/paths/az-104-administrator-prerequisites/"),
        ("AZ-104: Identities and governance", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/paths/az-104-manage-identities-governance/"),
    ],
    "Azure - Redes, Compute e Storage": [
        ("AZ-104: Compute resources", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/paths/az-104-manage-compute-resources/"),
        ("Curso AZ-104T00", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/courses/az-104t00"),
    ],
    "Azure - Monitoramento, Backup e Custos": [
        ("Certificação Azure Administrator", "Microsoft", "https://learn.microsoft.com/pt-br/credentials/certifications/azure-administrator/"),
    ],
    "Terraform": [
        ("Get Started - Azure", "HashiCorp Developer", "https://developer.hashicorp.com/terraform/tutorials/azure-get-started"),
    ],
    "Linux para Cloud": [
        ("Linux Unhatched", "Cisco Skills for All", "https://skillsforall.com/course/linux-unhatched"),
        ("Introduction to Linux", "Linux Foundation - edX", "https://www.edx.org/learn/linux/the-linux-foundation-introduction-to-linux"),
    ],
    "Docker e Docker Compose": [
        ("Docker Get Started", "Docker Docs", "https://docs.docker.com/get-started/"),
        ("Docker Compose", "Docker Docs", "https://docs.docker.com/compose/"),
        ("Docker Compose Quickstart", "Docker Docs", "https://docs.docker.com/compose/gettingstarted/"),
    ],
    "GitHub Actions e CI/CD": [
        ("Introduction to GitHub Actions", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/modules/introduction-to-github-actions/"),
        ("Automate workflow with GitHub Actions - Part 1", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/paths/github-actions/"),
        ("Automate workflow with GitHub Actions - Part 2", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/paths/github-actions-2/"),
        ("Deploy applications to Azure with GitHub Actions", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/modules/github-actions-cd/"),
    ],
}

PROJECTS = [
    ("Rede Hospitalar no Packet Tracer", "Redes", "Topologia com setores, VLANs, DHCP, DNS, roteamento e regras de acesso.", "Arquivo Packet Tracer, diagrama, plano IP e testes.", "Redes, troubleshooting e documentação.", "Analista de Infraestrutura", ["Packet Tracer", "Redes"]),
    ("Hospital Bulgaroni Lab", "Windows Server/AD", "Domínio com OUs, grupos, GPOs e pastas departamentais.", "README, diagrama, scripts e evidências sanitizadas.", "Windows Server, AD, GPO, DNS, DHCP e permissões.", "Infraestrutura Pleno", ["Windows Server", "Active Directory", "PowerShell"]),
    ("Kit PowerShell de Infraestrutura", "Automação", "Criação de usuários por CSV, auditoria de AD e inventário.", "Scripts .ps1, CSV exemplo, logs e documentação.", "PowerShell, automação e rastreabilidade.", "Infraestrutura/Cloud", ["PowerShell", "GitHub"]),
    ("Hospital Híbrido Azure", "Azure", "Ambiente segmentado com identidade, redes, VMs, storage e monitoramento.", "Arquitetura, runbook, evidências e controle de custos.", "Azure, RBAC, VNet, NSG, VMs, Monitor e Backup.", "Cloud Jr/Azure Admin", ["Azure", "Redes", "Monitoramento"]),
    ("Azure com Terraform", "IaC", "Provisionamento reproduzível do laboratório Azure.", "Código .tf, variables, outputs e instruções de apply/destroy.", "Terraform, IaC, Git e Azure.", "Cloud/DevOps Jr", ["Terraform", "Azure", "GitHub"]),
    ("Intranet Django Containerizada", "Docker", "Versão sem dados corporativos com Django, PostgreSQL e Nginx.", "Dockerfile, compose, .env.example e documentação.", "Docker, Compose, Linux e aplicações.", "Cloud/DevOps Jr", ["Docker", "Django", "PostgreSQL", "Nginx"]),
    ("Pipeline CI/CD", "GitHub Actions", "Testar, construir e publicar a aplicação automaticamente.", "Workflow YAML, badges, logs e documentação.", "CI/CD, GitHub Actions e automação.", "DevOps Jr", ["GitHub Actions", "Docker", "CI/CD"]),
    ("Plataforma Hospitalar Integrada", "Projeto final", "Caso completo unindo ambiente local, cloud, IaC, containers e pipeline.", "Repositório principal, vídeo curto, diagramas e estudo de caso.", "Arquitetura, execução e comunicação técnica.", "Infra Pleno/Cloud Jr", ["Azure", "Terraform", "Docker", "GitHub Actions"]),
]

TRACK_CATEGORY = {
    "Fundamentos de Redes": Trilha.Categoria.REDES,
    "Windows Server e Active Directory": Trilha.Categoria.WINDOWS,
    "PowerShell para Infraestrutura": Trilha.Categoria.POWERSHELL,
    "Git e GitHub": Trilha.Categoria.DEVOPS,
    "Azure - Identidade e Governança": Trilha.Categoria.AZURE,
    "Azure - Redes, Compute e Storage": Trilha.Categoria.AZURE,
    "Azure - Monitoramento, Backup e Custos": Trilha.Categoria.AZURE,
    "Terraform": Trilha.Categoria.DEVOPS,
    "Linux para Cloud": Trilha.Categoria.DEVOPS,
    "Docker e Docker Compose": Trilha.Categoria.DEVOPS,
    "GitHub Actions e CI/CD": Trilha.Categoria.DEVOPS,
    "Projeto Integrado e Empregabilidade": Trilha.Categoria.OUTRO,
}


class Command(BaseCommand):
    help = "Substitui os dados pessoais pelo PDI gratuito de Infraestrutura Cloud."

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirma a exclusão dos dados atuais do PDI.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Refaz o plano mesmo quando ele já existe (também apaga o progresso).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["confirm"]:
            raise CommandError("Use --confirm para autorizar a substituição dos dados.")

        usuario = Usuario.objects.filter(pk=1).first()
        if usuario is None:
            raise CommandError("O usuário pessoal ainda não foi configurado.")

        existente = Roadmap.objects.filter(
            usuario=usuario,
            observacoes__contains=PLAN_MARKER,
        ).first()
        if existente and not options["force"]:
            self.stdout.write(
                self.style.SUCCESS(
                    "Plano Infra Cloud já instalado; progresso atual preservado."
                )
            )
            return

        self._delete_current_data(usuario)
        objetivo = self._create_objective(usuario)
        self._create_roadmap(usuario, objetivo)
        self._create_studies(usuario, objetivo)
        self._create_projects(usuario, objetivo)
        self._update_profile(usuario)

        self.stdout.write(
            self.style.SUCCESS(
                "PDI substituído: 48 semanas, 12 fases, 8 projetos e recursos gratuitos."
            )
        )

    def _delete_current_data(self, usuario):
        file_refs = []
        for item in MaterialPDF.objects.filter(usuario=usuario):
            if item.arquivo.name:
                file_refs.append((item.arquivo.storage, item.arquivo.name))
        for item in Evidencia.objects.filter(usuario=usuario):
            if item.imagem.name:
                file_refs.append((item.imagem.storage, item.imagem.name))
        for item in FonteRoadmap.objects.filter(usuario=usuario):
            if item.arquivo.name:
                file_refs.append((item.arquivo.storage, item.arquivo.name))

        AcaoRevisao.objects.filter(usuario=usuario).delete()
        RevisaoPeriodica.objects.filter(usuario=usuario).delete()
        EvidenciaCompetencia.objects.filter(usuario=usuario).delete()
        AvaliacaoCompetencia.objects.filter(usuario=usuario).delete()
        Competencia.objects.filter(usuario=usuario).delete()
        Certificacao.objects.filter(usuario=usuario).delete()
        Anotacao.objects.filter(usuario=usuario).delete()
        MaterialPDF.objects.filter(usuario=usuario).delete()
        Evidencia.objects.filter(usuario=usuario).delete()
        ProjetoTecnologia.objects.filter(usuario=usuario).delete()
        TarefaProjeto.objects.filter(usuario=usuario).delete()
        MarcoProjeto.objects.filter(usuario=usuario).delete()
        Projeto.objects.filter(usuario=usuario).delete()
        Tecnologia.objects.filter(usuario=usuario).delete()
        Roadmap.objects.filter(usuario=usuario).delete()
        FonteRoadmap.objects.filter(usuario=usuario).delete()
        Aula.objects.filter(usuario=usuario).delete()
        Disciplina.objects.filter(usuario=usuario).delete()
        Periodo.objects.filter(usuario=usuario).delete()
        Curso.objects.filter(usuario=usuario).delete()
        Trilha.objects.filter(usuario=usuario).delete()
        Objetivo.objects.filter(usuario=usuario).delete()
        Tag.objects.filter(usuario=usuario).delete()

        def remove_files():
            for storage, name in file_refs:
                if storage.exists(name):
                    storage.delete(name)

        transaction.on_commit(remove_files)

    def _create_objective(self, usuario):
        objetivo = Objetivo.objects.create(
            usuario=usuario,
            titulo="Tornar-me Analista de Infraestrutura Pleno com domínio de Azure e automação",
            descricao=(
                "Plano gratuito de 48 semanas para consolidar infraestrutura, "
                "evoluir para Cloud Operations e avançar para Cloud Engineer ou DevOps."
            ),
            categoria=Objetivo.Categoria.PROFISSIONAL,
            motivo=(
                "Transformar experiência prática em laboratórios, código, documentação "
                "e evidências apresentáveis em entrevistas."
            ),
            data_inicio=PLAN_START,
            prazo=PLAN_START + timedelta(weeks=47, days=6),
            prioridade=Objetivo.Prioridade.ALTA,
            status=Objetivo.Status.PLANEJADO,
            progresso=0,
            resultado_esperado=(
                "Atuar como Analista de Infraestrutura Pleno com domínio prático "
                "de Azure e automação, preparado para Cloud Engineer ou DevOps."
            ),
            evidencia_esperada=(
                "Oito projetos publicados com laboratório, código, README, "
                "diagramas, testes e demonstrações."
            ),
            proxima_acao="Iniciar a Semana 1: IPv4, máscara, gateway e subnetting.",
            observacoes=(
                "Carga planejada: 8 horas por semana, 384 horas no total. "
                "Curso assistido não conta como conclusão; laboratório, código "
                "e documentação contam."
            ),
        )
        for nome, slug in (
            ("Infraestrutura", "infraestrutura"),
            ("Azure", "azure"),
            ("Automação", "automacao"),
            ("Cloud", "cloud"),
        ):
            tag = Tag.objects.create(usuario=usuario, nome=nome, slug=slug)
            objetivo.tags.add(tag)
        return objetivo

    def _create_roadmap(self, usuario, objetivo):
        roadmap = Roadmap.objects.create(
            usuario=usuario,
            nome="PDI - Infraestrutura Cloud com Automação",
            descricao=(
                "Trilha gratuita de 48 semanas: estudo, prática, portfólio e currículo."
            ),
            objetivo=objetivo,
            data_inicio=PLAN_START,
            prazo=PLAN_START + timedelta(weeks=47, days=6),
            status=Roadmap.Status.PLANEJADO,
            prioridade=Roadmap.Prioridade.ALTA,
            observacoes=(
                "8 horas por semana, aproximadamente 384 horas. "
                "Conclua cada semana pelo botão ao lado da atividade. "
                f"{PLAN_MARKER}"
            ),
        )

        tracks = list(dict.fromkeys(week[0] for week in WEEKS))
        for phase_order, track in enumerate(tracks, start=1):
            indexes = [i for i, week in enumerate(WEEKS, start=1) if week[0] == track]
            first_week, last_week = min(indexes), max(indexes)
            start = PLAN_START + timedelta(weeks=first_week - 1)
            end = PLAN_START + timedelta(weeks=last_week - 1, days=6)
            project_name = WEEKS[first_week - 1][2]
            curriculum_gain = WEEKS[first_week - 1][3]
            phase = FaseRoadmap.objects.create(
                usuario=usuario,
                roadmap=roadmap,
                titulo=f"{first_week:02d}-{last_week:02d} · {track}",
                descricao=curriculum_gain,
                ordem=phase_order,
                data_prevista_inicio=start,
                data_prevista_conclusao=end,
                criterios_conclusao=(
                    "Explicar o conceito, configurar o cenário, provocar e "
                    "diagnosticar uma falha e publicar evidência sem dados corporativos."
                ),
                dependencias=(
                    f"Conclusão da fase {phase_order - 1}."
                    if phase_order > 1
                    else "Nenhuma dependência."
                ),
                proxima_acao=WEEKS[first_week - 1][1],
            )
            for week_number in indexes:
                _, action, project, gain = WEEKS[week_number - 1]
                week_start = PLAN_START + timedelta(weeks=week_number - 1)
                EtapaRoadmap.objects.create(
                    usuario=usuario,
                    fase=phase,
                    titulo=f"Semana {week_number:02d} — {action}",
                    descricao=(
                        f"Início: {week_start:%d/%m/%Y} · 8 horas. "
                        f"Projeto: {project}. Ganho no currículo: {gain}"
                    ),
                    ordem=week_number - first_week + 1,
                )
            EntregaRoadmap.objects.create(
                usuario=usuario,
                fase=phase,
                titulo=project_name,
                descricao=(
                    "Entrega prática da fase. Registre laboratório, código, "
                    "documentação, decisões e evidências."
                ),
                criterio_aceite=(
                    "Material publicável e explicável em entrevista, sem dados reais da empresa."
                ),
            )
        return roadmap

    def _create_studies(self, usuario, objetivo):
        course = Curso.objects.create(
            usuario=usuario,
            nome="PDI - Infraestrutura Cloud com Automação",
            instituicao="Plano pessoal com recursos gratuitos",
            tipo=Curso.Tipo.LIVRE,
            descricao="48 semanas, 384 horas e foco em prática demonstrável.",
            data_inicio=PLAN_START,
            data_prevista_conclusao=PLAN_START + timedelta(weeks=47, days=6),
            status=StatusEstudo.PLANEJADO,
            carga_horaria=384,
            observacoes=(
                "Rotina semanal: 3h de teoria, 2h de laboratório, "
                "2h de projeto e 1h de documentação."
            ),
        )
        period = Periodo.objects.create(
            usuario=usuario,
            curso=course,
            nome="Plano completo de 48 semanas",
            numero=1,
            data_inicio=PLAN_START,
            data_conclusao=PLAN_START + timedelta(weeks=47, days=6),
            status=StatusEstudo.PLANEJADO,
        )
        tracks = list(dict.fromkeys(week[0] for week in WEEKS))
        for order, track in enumerate(tracks, start=1):
            week_numbers = [
                index for index, week in enumerate(WEEKS, start=1) if week[0] == track
            ]
            hours = len(week_numbers) * 8
            track_obj = Trilha.objects.create(
                usuario=usuario,
                titulo=f"{order:02d} · {track}",
                descricao=WEEKS[week_numbers[0] - 1][3],
                categoria=TRACK_CATEGORY[track],
                nivel=Trilha.Nivel.INTERMEDIARIO,
                prioridade="alta" if order <= 7 else "media",
                data_inicio=PLAN_START + timedelta(weeks=week_numbers[0] - 1),
                prazo=PLAN_START + timedelta(weeks=week_numbers[-1] - 1, days=6),
                status=StatusEstudo.PLANEJADO,
                progresso=0,
                carga_horaria_prevista=hours,
                objetivo=objetivo,
                observacoes="Concluir com laboratório, código ou documentação.",
            )
            course.trilhas.add(track_obj)
            resource_text = "\n".join(
                f"{name} — {platform}: {url}"
                for name, platform, url in RESOURCES.get(track, [])
            )
            discipline = Disciplina.objects.create(
                usuario=usuario,
                curso=course,
                periodo=period,
                nome=f"{order:02d} · {track}",
                codigo=f"PDI-{order:02d}",
                descricao=WEEKS[week_numbers[0] - 1][3],
                carga_horaria=hours,
                status=StatusEstudo.PLANEJADO,
                progresso=0,
                ementa="; ".join(WEEKS[i - 1][1] for i in week_numbers),
                observacoes=resource_text,
            )
            for content_number, week_number in enumerate(week_numbers, start=1):
                _, action, project, gain = WEEKS[week_number - 1]
                Aula.objects.create(
                    usuario=usuario,
                    disciplina=discipline,
                    titulo=f"Semana {week_number:02d} — {action}",
                    numero=content_number,
                    data=PLAN_START + timedelta(weeks=week_number - 1),
                    descricao=f"Projeto associado: {project}. {gain}",
                    status=StatusEstudo.PLANEJADO,
                    duracao_prevista=480,
                    tags=f"pdi, semana {week_number}, {track.lower()}",
                )

    def _create_projects(self, usuario, objetivo):
        tech_cache = {}
        for index, (
            title,
            area,
            scope,
            deliverables,
            skills,
            target_role,
            technologies,
        ) in enumerate(PROJECTS, start=1):
            project = Projeto.objects.create(
                usuario=usuario,
                titulo=f"P{index} · {title}",
                objetivo=objetivo,
                problema=scope,
                solucao=(
                    f"Entregáveis: {deliverables}\n"
                    f"Competências comprovadas: {skills}\n"
                    f"Vaga beneficiada: {target_role}"
                ),
                data_inicio=PLAN_START,
                prazo=PLAN_START + timedelta(weeks=min(48, index * 6) - 1, days=6),
                status=Projeto.Status.PLANEJADO,
                progresso=0,
                aprendizados=f"Área principal: {area}.",
            )
            tasks = [item.strip().rstrip(".") for item in deliverables.split(",")]
            for order, task in enumerate(tasks, start=1):
                TarefaProjeto.objects.create(
                    usuario=usuario,
                    projeto=project,
                    titulo=task[:180],
                    descricao=f"Entregável previsto no plano para {title}.",
                    status=TarefaProjeto.Status.PENDENTE,
                    prioridade=TarefaProjeto.Prioridade.ALTA,
                    ordem=order,
                )
            MarcoProjeto.objects.create(
                usuario=usuario,
                projeto=project,
                titulo="Projeto documentado e demonstrável",
                descricao=(
                    "Código ou laboratório validado, README, diagrama, evidências "
                    "e aprendizados prontos para entrevista."
                ),
                prazo=project.prazo,
                status=MarcoProjeto.Status.PENDENTE,
                ordem=1,
            )
            for technology_name in technologies:
                if technology_name not in tech_cache:
                    tech_cache[technology_name] = Tecnologia.objects.create(
                        usuario=usuario,
                        nome=technology_name,
                        categoria=(
                            Tecnologia.Categoria.NUVEM
                            if technology_name == "Azure"
                            else Tecnologia.Categoria.FERRAMENTA
                        ),
                    )
                ProjetoTecnologia.objects.create(
                    usuario=usuario,
                    projeto=project,
                    tecnologia=tech_cache[technology_name],
                )

    def _update_profile(self, usuario):
        usuario.cargo_desejado = (
            "Analista de Infraestrutura Pleno — Cloud Azure e automação"
        )
        usuario.objetivo_principal = (
            "Concluir o PDI de Infraestrutura Cloud com Automação em 48 semanas."
        )
        usuario.save(
            update_fields=("cargo_desejado", "objetivo_principal", "updated_at")
        )
