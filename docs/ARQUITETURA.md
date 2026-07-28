# Arquitetura

## Visão de contexto

```mermaid
C4Context
    title Contexto do Meu PDI
    Person(kauan, "Kauan", "Mantém o PDI na instalação pessoal")
    Person(recrutador, "Recrutador", "Navega na demonstração somente leitura")
    System(pdi, "Meu PDI", "Planejamento e evidências de desenvolvimento")
    System_Ext(sentry, "Sentry", "Erros e desempenho, quando configurado")
    Rel(kauan, pdi, "Registra e acompanha")
    Rel(recrutador, pdi, "Consulta resultados")
    Rel(pdi, sentry, "Envia telemetria sem PII")
```

## Contêineres

```mermaid
flowchart TB
    B["Navegador<br/>HTML, CSS, JavaScript"] -->|HTTPS| G["Gunicorn<br/>servidor WSGI"]
    G --> D["Django 5.2 LTS<br/>aplicação modular"]
    D --> PG[("PostgreSQL<br/>dados estruturados")]
    D --> FS["Armazenamento privado<br/>PDFs e capturas"]
    D --> ST["WhiteNoise<br/>arquivos estáticos"]
    D --> LOG["stdout<br/>logs JSON"]
    D -.-> SEN["Sentry opcional"]
    HC["Monitor da plataforma"] -->|GET /health/ready/| D
```

## Módulos de domínio

```mermaid
flowchart LR
    usuarios --> objetivos
    objetivos --> roadmap
    objetivos --> projetos
    estudos --> anotacoes
    estudos --> biblioteca
    projetos --> competencias
    competencias --> revisoes
    estudos --> certificacoes
    objetivos --> indicadores
    roadmap --> indicadores
    projetos --> indicadores
    competencias --> indicadores
    revisoes --> indicadores
    certificacoes --> indicadores
```

Cada módulo mantém sua própria camada de persistência e interface. Consultas
consolidadas ficam em `selectors.py`; regras que alteram vários registros ficam
em `services.py`; views coordenam HTTP e templates.

## Decisões

| Decisão | Justificativa | Consequência |
| --- | --- | --- |
| Monólito modular | Escopo pessoal e implantação simples | Uma unidade de deploy |
| Server-side rendering | Menos complexidade e boa acessibilidade | Interações ricas pontuais |
| PostgreSQL em produção | Integridade e operação gerenciada | Requer serviço de banco |
| SQLite local | Instalação rápida no Windows | Não é usado no deploy público |
| Demo pública somente leitura | Não há autenticação por escolha do produto | Recrutadores navegam sem risco de alteração |
| Upload privado | PDFs e evidências podem conter dados sensíveis | Acesso sempre passa por autorização |
| Logs em stdout | Compatível com contêineres e plataformas | Retenção pertence à plataforma |

## Fluxo de implantação

```mermaid
sequenceDiagram
    participant Git as Repositório
    participant Build as Build
    participant DB as PostgreSQL
    participant Web as Serviço web
    participant Mon as Monitor
    Git->>Build: novo commit
    Build->>Build: instalar e coletar estáticos
    Build->>DB: aplicar migrations e seeds
    Build->>Web: iniciar Gunicorn
    Mon->>Web: GET /health/ready/
    Web->>DB: SELECT 1
    DB-->>Web: disponível
    Web-->>Mon: 200 OK
```
