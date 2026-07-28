# Meu PDI — Planejamento técnico

## 1. Escopo e análise funcional

O Meu PDI organiza desenvolvimento pessoal, acadêmico e profissional em um fluxo
rastreável:

`objetivo → roadmap → estudo → anotação → prática → evidência → indicador`

### Perfis e contexto

- O sistema é pessoal, local e possui um único perfil criado automaticamente.
- Não há cadastro, login, senha, logout ou recuperação de acesso.
- Todos os registros mantêm um proprietário interno apenas para integridade dos
  relacionamentos e eventual migração futura, sem expor gestão de usuários.
- O conteúdo demonstrativo é carregado por comando de seed e pode ser editado.
- O produto é privado por padrão. Publicação em portfólio exige consentimento
  explícito e pertence a uma fase posterior.

### Capacidades do MVP

1. Acesso local direto, perfil e preferências.
2. Objetivos com prazos, filtros, status e progresso.
3. Roadmaps com fases, etapas e entregas.
4. Trilhas, cursos, períodos, disciplinas, aulas e sessões de estudo.
5. Upload e visualização protegida de PDF.
6. Anotações ricas, versões e vínculo com página do PDF.
7. Projetos, tecnologias, evidências e progresso.
8. Dashboard com indicadores básicos e dados do próprio usuário.

### Fora do MVP

Flashcards, modo prova, IA, notificações externas, portfólio automático,
currículo gerado, revisão espaçada, Celery, Redis, API pública e integrações
externas.

## 2. Arquitetura proposta

### Estilo

- Monólito modular Django, com apps por domínio.
- Renderização server-side com Django Templates.
- Bootstrap 5 e Bootstrap Icons para o sistema visual.
- HTMX para respostas parciais; operações essenciais continuam funcionando sem
  JavaScript.
- JavaScript pequeno e progressivo para tema, menu e editor.
- Camada de `services` para comandos e regras de negócio.
- Camada de `selectors` para consultas compostas e otimizadas.
- Django Forms para entrada e validação.
- Django ORM como única camada de persistência do MVP.
- SQLite em desenvolvimento e PostgreSQL em produção por configuração.

### Camadas

| Camada | Responsabilidade |
| --- | --- |
| Templates/static | Apresentação, acessibilidade e melhoria progressiva |
| Views/forms | Fluxo HTTP, autorização, validação e mensagens |
| Services | Transações, cálculos e mudanças de estado |
| Selectors | Consultas filtradas por proprietário e otimizações |
| Models | Integridade estrutural, constraints e comportamento local |
| Storage | Arquivos privados e validação de uploads |

### Decisões principais

- `AUTH_USER_MODEL` personalizado desde a primeira migração.
- UUID como chave pública de entidades expostas em URLs; IDs internos não são
  aceitos como prova de autorização.
- `PROTECT` quando apagar o pai causaria perda de contexto; arquivamento para
  registros de negócio; `CASCADE` apenas para filhos sem significado próprio.
- Valores monetários e duração são relacionais/numéricos, nunca JSON.
- Rich text é sanitizado no servidor por allowlist antes de persistir.
- Arquivos são servidos por view autorizada em desenvolvimento. Em produção,
  a autorização pode emitir URL temporária do object storage.
- Sem DRF no MVP: não existe consumidor externo que justifique uma API.

## 3. Apps Django

| App | Responsabilidade | Fase |
| --- | --- | --- |
| `core` | dashboard, base abstrata, auditoria, busca e componentes | Fundação/MVP |
| `usuarios` | perfil pessoal, preferências e proprietário interno | Fundação |
| `objetivos` | objetivos, tags e histórico de progresso | MVP |
| `roadmap` | roadmaps, fases, etapas e entregas | MVP |
| `estudos` | trilhas, cursos, períodos, disciplinas, aulas e sessões | MVP |
| `anotacoes` | notas ricas, versões e autosave | MVP |
| `biblioteca` | arquivos, PDFs, links e acesso protegido | MVP |
| `projetos` | projetos, marcos, tarefas, tecnologias e evidências | MVP |
| `competencias` | matriz, avaliações e evidências | Pós-MVP inicial |
| `certificacoes` | planejamento e resultados de certificações | Pós-MVP |
| `revisoes` | revisões periódicas e ações futuras | Pós-MVP |
| `indicadores` | agregações, métricas e gráficos | Dashboard/MVP |
| `portfolio` | projeção pública explicitamente selecionada | Pós-MVP |

Na fundação, somente `core` e `usuarios` terão modelos e rotas funcionais. Os
demais apps entram na etapa do domínio correspondente, evitando shells vazios
que pareçam recursos concluídos.

## 4. Entidades, campos e relacionamentos

Campos comuns das entidades de negócio: `id` UUID, `usuario`, `created_at`,
`updated_at`, `arquivado_em` quando aplicável.

### Identidade

- **Usuario**: email, nome, cargo atual, cargo desejado, objetivo principal,
  timezone, idioma, tema, flags de acesso. Um usuário possui todos os registros.
- **PreferenciaUsuario**: usuário 1:1, menu recolhido, início da semana,
  pesos do progresso geral e preferências de notificação.

### Objetivos

- **Objetivo**: título, descrição, categoria, motivo, início, prazo, prioridade,
  status, progresso, resultado/evidência esperados, próxima ação, obstáculos,
  observações e conclusão.
- **HistoricoObjetivo**: objetivo N:1, autor, tipo de mudança, valor anterior,
  valor novo e data.
- **Tag**: nome e slug por usuário. Relação N:N com entidades que aceitam tags
  por tabelas intermediárias explícitas.

### Roadmap

- **Roadmap**: usuário, objetivo N:1 opcional, nome, datas, status, progresso,
  prioridade e observações.
- **FaseRoadmap**: roadmap N:1, ordem, título, datas, status, progresso,
  critérios, dependências e próxima ação.
- **EtapaRoadmap**: fase N:1, ordem, título, datas, status, progresso.
- **EntregaRoadmap**: fase ou etapa N:1, descrição, evidência, prazo e conclusão.

### Estudos

- **Trilha**: usuário, objetivo opcional, categoria, nível, prioridade, datas,
  status, progresso, cargas horárias, pré-requisitos, capa e observações.
- **ModuloTrilha**: trilha N:1, ordem, título, progresso.
- **Curso**: usuário, nome, instituição, tipo, datas, status, carga e imagem.
- **Periodo**: curso N:1, número, nome, datas e status.
- **Disciplina**: curso N:1, período N:1 opcional, professor, carga, nota,
  frequência, progresso, ementa e status.
- **Aula**: disciplina N:1, módulo opcional, número, data, durações,
  dificuldade, status, resumo, dúvidas, aplicação, revisão, flags e conclusão.
- **SessaoEstudo**: usuário, vínculos opcionais com trilha/curso/disciplina/aula,
  início, fim, duração, foco, aprendizado, dificuldades e observações.

Trilha e curso são conceitos distintos. Uma trilha pode agregar cursos e aulas
por relações intermediárias com ordem e peso, sem duplicar os registros.

### Biblioteca e anotações

- **Material**: usuário, título, descrição, tipo, arquivo ou URL, relações
  opcionais com curso/disciplina/aula/projeto, metadados, favorito e status.
- **Anotacao**: usuário, aula N:1, disciplina derivada, título, HTML sanitizado,
  texto pesquisável, tipo, página, trecho, favorita e status de revisão.
- **VersaoAnotacao**: anotação N:1, número, HTML sanitizado, texto, autor e data.
- **AnexoAnotacao**: anotação N:1 e material N:1.

Um PDF de aula é um `Material` relacionado à aula e marcado como principal por
uma relação `MaterialAula`; o binário não é duplicado.

### Projetos e competências

- **Projeto**: usuário, objetivo opcional, título, problema, solução, datas,
  status, progresso, resultado, aprendizados e visibilidade.
- **Tecnologia**: catálogo por usuário; relação N:N com projeto.
- **MarcoProjeto** e **TarefaProjeto**: filhos ordenados com prazo e status.
- **Evidencia**: usuário, projeto opcional, tipo, descrição, material opcional,
  URL, data e validação.
- **Competencia**: usuário, nome, categoria, níveis 1–5, critérios e datas.
- **AvaliacaoCompetencia**: competência N:1, nível, justificativa e data.
- **EvidenciaCompetencia**: avaliação N:N evidência. Uma elevação de nível exige
  ao menos uma evidência.

### Certificações e revisões

- **Certificacao**: usuário, instituição, código, status, prioridade, datas,
  custos, nota, links, material certificado, trilha e objetivo.
- **RevisaoPeriodica**: usuário, tipo, período, respostas, status e conclusão.
  As respostas são campos relacionais ou uma tabela `RespostaRevisao`, evitando
  um JSON opaco.
- **AcaoRevisao**: revisão N:1, descrição, prazo, status e vínculos de domínio.
- **RevisaoConteudo**: usuário, aula ou anotação, datas, resultado e domínio.

### Auditoria e notificações

- **EventoAuditoria**: usuário executor, ação, tipo/UUID do objeto, resumo
  seguro, IP mascarável e data. Nunca guarda senha, token ou conteúdo integral.
- **Notificacao**: destinatário, tipo, título, link interno, leitura e data.

## 5. Cardinalidades resumidas

```text
Usuario 1 ─── 1 PreferenciaUsuario
Usuario 1 ─── N Objetivo 1 ─── N HistoricoObjetivo
Objetivo 1 ─── N Roadmap 1 ─── N FaseRoadmap
FaseRoadmap 1 ─── N EtapaRoadmap
Fase/Etapa 1 ─── N EntregaRoadmap

Usuario 1 ─── N Trilha 1 ─── N ModuloTrilha
Usuario 1 ─── N Curso 1 ─── N Periodo
Curso 1 ─── N Disciplina N ─── 0..1 Periodo
Disciplina 1 ─── N Aula
Usuario 1 ─── N SessaoEstudo

Aula 1 ─── N Anotacao 1 ─── N VersaoAnotacao
Usuario 1 ─── N Material
Aula N ─── N Material (MaterialAula)
Anotacao N ─── N Material (AnexoAnotacao)

Usuario 1 ─── N Projeto 1 ─── N MarcoProjeto
Projeto 1 ─── N TarefaProjeto
Projeto N ─── N Tecnologia
Projeto 1 ─── N Evidencia

Usuario 1 ─── N Competencia 1 ─── N AvaliacaoCompetencia
AvaliacaoCompetencia N ─── N Evidencia
Usuario 1 ─── N Certificacao
Usuario 1 ─── N RevisaoPeriodica 1 ─── N AcaoRevisao
```

## 6. Índices, constraints e exclusões

### Índices

- Todos os filtros começam por `usuario_id`.
- Compostos: `(usuario, status)`, `(usuario, prazo)`,
  `(usuario, status, prazo)`, `(usuario, updated_at)`.
- Ordem única: `(roadmap, ordem)`, `(fase, ordem)`, `(trilha, ordem)`.
- Aula: `(usuario, disciplina, data)` e `(usuario, concluida, data)`.
- Sessão: `(usuario, inicio)` e `(usuario, fim)`.
- Anotação: `(usuario, aula, updated_at)`; PostgreSQL ganhará índice GIN de
  full-text em migração específica futura.
- Material: `(usuario, tipo, created_at)` e hash do arquivo para deduplicação.
- Tags e tecnologias: unique case-insensitive por usuário.

### Constraints

- Progresso entre 0 e 100.
- Níveis de competência e foco dentro das escalas definidas.
- Fim maior ou igual ao início.
- Carga e duração não negativas.
- Somente um PDF principal por aula.
- Somente uma sessão aberta por usuário; no PostgreSQL, unique constraint
  parcial. No SQLite, validação transacional complementar.
- Objeto público exige `publicado_em` e confirmação explícita.

### Regras de exclusão

| Relação | Política |
| --- | --- |
| Usuário → dados | `PROTECT` operacional; remoção de conta usa processo dedicado |
| Objetivo → roadmap/projeto | `PROTECT` enquanto filhos ativos existirem |
| Roadmap → fases → etapas | Arquivamento; purge administrativo pode usar cascade |
| Curso → disciplina → aula | `PROTECT`/arquivamento para preservar histórico |
| Aula → anotação | `PROTECT`; anotação pode ser reatribuída ou arquivada |
| Material → arquivo | Apaga binário apenas quando nenhuma relação o referencia |
| Anotação → versões | `CASCADE` somente no purge definitivo |
| Projeto → evidência | `PROTECT` para não destruir comprovação |

## 7. Mapa de URLs

O acesso local abre diretamente no único perfil pessoal. Rotas com objetos usam
UUID e queryset filtrado pelo proprietário interno.

```text
/                              core:home
/dashboard/                    core:dashboard
/buscar/                       core:busca

/conta/perfil/                 usuarios:perfil
/conta/preferencias/           usuarios:preferencias

/objetivos/                    objetivos:lista
/objetivos/novo/               objetivos:criar
/objetivos/<uuid>/             objetivos:detalhe
/objetivos/<uuid>/editar/      objetivos:editar
/objetivos/<uuid>/arquivar/    objetivos:arquivar

/roadmaps/                     roadmap:lista
/roadmaps/<uuid>/              roadmap:detalhe
/roadmaps/<uuid>/fases/nova/   roadmap:fase_criar

/estudos/trilhas/              estudos:trilha_lista
/estudos/cursos/               estudos:curso_lista
/estudos/disciplinas/          estudos:disciplina_lista
/estudos/aulas/                estudos:aula_lista
/estudos/aulas/<uuid>/         estudos:aula_detalhe
/estudos/sessoes/              estudos:sessao_lista

/biblioteca/                   biblioteca:lista
/biblioteca/upload/            biblioteca:upload
/biblioteca/<uuid>/abrir/      biblioteca:abrir_protegido
/biblioteca/<uuid>/baixar/     biblioteca:baixar

/anotacoes/                    anotacoes:lista
/anotacoes/<uuid>/             anotacoes:editar
/anotacoes/<uuid>/autosave/    anotacoes:autosave
/anotacoes/<uuid>/versoes/     anotacoes:versoes

/projetos/                     projetos:lista
/projetos/<uuid>/              projetos:detalhe
```

Endpoints HTMX mantêm a mesma regra de autorização e retornam parciais apenas
quando `HX-Request` está presente; caso contrário, redirecionam ou renderizam a
página completa.

## 8. Estrutura de diretórios

```text
dash/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── core/
├── usuarios/
├── objetivos/
├── roadmap/
├── estudos/
├── anotacoes/
├── biblioteca/
├── projetos/
├── competencias/
├── certificacoes/
├── revisoes/
├── indicadores/
├── portfolio/
├── templates/
│   ├── base.html
│   ├── components/
│   └── registration/
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── media/
├── docs/
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## 9. Permissões e segurança

### Matriz

| Ação | Acesso local |
| --- | ---: |
| Abrir dashboard | Direto |
| Ver/editar perfil pessoal | Sim |
| CRUD de registros pessoais | Sim |
| Abrir arquivos pessoais | Sim |
| Publicar projeto | Consentimento explícito |
| Gerenciar usuários | Não existe |

### Controles

- Querysets sempre escopados por `request.user`; o proprietário vem da sessão,
  nunca do formulário.
- CSRF em toda mutação, inclusive HTMX.
- Cookies `Secure`, `HttpOnly` e `SameSite=Lax` em produção.
- HSTS, redirecionamento HTTPS, `X-Content-Type-Options`, proteção de frame e
  política de referrer em produção.
- Uploads por allowlist de extensão + MIME detectado + tamanho; nome aleatório;
  armazenamento fora de static.
- HTML rico sanitizado por allowlist.
- O servidor local deve escutar apenas em `127.0.0.1`; o modo sem senha não pode
  ser exposto à rede ou à internet.
- Rate limiting e antivírus de upload são itens de hardening antes de SaaS.
- Segredos exclusivamente por ambiente.

## 10. Regras de negócio

1. Todo registro de domínio pertence a um usuário.
2. Relações só podem apontar para registros do mesmo usuário.
3. Progresso permanece entre 0 e 100.
4. Conclusão define data; reabertura registra histórico e não apaga auditoria.
5. Status atrasado é derivado de prazo vencido + não concluído; não depende de
   tarefa manual.
6. Progresso geral usa pesos configuráveis e cobertura mínima:

   ```text
   geral = Σ(score_domínio × peso_domínio) / Σ(pesos de domínios com dados)
   ```

   Pesos iniciais: objetivos 25%, trilhas 20%, aulas 15%, projetos 20%,
   revisões 10%, competências 10%. Domínio sem dados não aumenta o resultado;
   a interface mostra cobertura do cálculo para evitar falsa precisão.
7. Trilha calcula progresso por itens ponderados, com override manual auditado.
8. Competência não sobe por consumo de conteúdo; avaliação exige evidência.
9. Sessões simultâneas do mesmo usuário são recusadas.
10. O arquivo físico só é apagado sem referências remanescentes.
11. Datas incoerentes são recusadas, salvo fluxo explícito com justificativa.
12. Arquivamento é padrão para registros com histórico.

## 11. Componentes visuais

- Shell com sidebar recolhível, topbar e área principal.
- Cabeçalho de página com breadcrumb, título, descrição e ação primária.
- KPI card, progress card, chart card e summary card.
- Tabela responsiva com filtros e ações acessíveis.
- Badges semânticos de status e prioridade.
- Timeline para roadmap.
- Form field com label, ajuda e erro.
- Empty state com uma próxima ação.
- Modal de confirmação com alternativa sem JavaScript.
- Toast/alert de mensagens Django.
- Paginação, anexos e skeleton apenas em carregamentos reais.

## 12. Layout sugerido do dashboard

### Desktop

```text
┌──────── Sidebar ────────┬──────────────────────────────────────────┐
│ Meu PDI                 │ Busca             Tema  Perfil           │
│ Dashboard               ├──────────────────────────────────────────┤
│ Objetivos               │ Olá, usuário              Nova ação     │
│ Roadmap                 │ Objetivo principal + progresso/cobertura │
│ Estudos                 ├─────────┬─────────┬─────────┬────────────┤
│ Biblioteca              │ Geral   │ Semana  │ Sequência│ Atrasadas │
│ Projetos                ├───────────────────┬──────────────────────┤
│ Indicadores             │ Horas por mês     │ Próximos prazos      │
│ Configurações           ├───────────────────┼──────────────────────┤
│                         │ Trilhas/competênc. │ Atividade recente    │
└─────────────────────────┴───────────────────┴──────────────────────┘
```

### Mobile

Topbar fixa com botão do menu; conteúdo em uma coluna; KPIs em carrossel
horizontal acessível ou grade 2×N; tabelas viram cards; ação principal permanece
visível sem cobrir o conteúdo.

## 13. Backlog priorizado

### P0 — Fundação

- Configuração por ambiente, proprietário local e acesso automático.
- Layout, navegação, tema e dashboard pessoal vazio.
- Testes de acesso direto e isolamento-base.
- README Windows, `.env`, static/media e checklist de produção.

### P1 — Fluxo central

- Objetivos completos.
- Roadmap, fases, etapas e progresso.
- Trilhas, cursos, períodos, disciplinas e aulas.
- Sessões de estudo e bloqueio de simultaneidade.

### P2 — Conhecimento e prática

- Upload protegido e visualizador PDF.js.
- Editor rico sanitizado, autosave e versões.
- Projetos, marcos, tarefas, tecnologias e evidências.
- Dashboard real com indicadores e prazos.

### P3 — Consolidação

- Competências com evidências.
- Revisões periódicas.
- Certificações.
- Busca global com ORM.

### P4 — Evolução

- Revisão espaçada, flashcards e modo prova.
- Portfólio e currículo por evidências.
- Notificações externas e integrações opcionais.

## 14. Divisão do MVP

1. **Fundação**: ambiente, perfil pessoal, acesso direto, shell e testes.
2. **Objetivos**: CRUD, filtros, prazo, progresso e histórico.
3. **Roadmap**: hierarquia, timeline, entregas e cálculo.
4. **Estudos**: hierarquia acadêmica, trilhas, aulas e sessões.
5. **PDF/anotações**: upload, acesso, viewer, rich text, autosave e versões.
6. **Dashboard**: selectors, KPIs, gráficos e atividades.
7. **Projetos**: prática, tecnologias, evidências e progresso.
8. **Aceite**: testes de ponta a ponta, segurança, responsividade e documentação.

Cada etapa só avança após migrations, checks e testes da anterior passarem.

## 15. Riscos técnicos e mitigação

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Escopo excessivo | MVP interminável | Gates por etapa e backlog P0–P4 |
| IDOR em URLs/arquivos | Vazamento grave | Queryset por usuário + testes adversariais |
| XSS no editor | Roubo de sessão | Sanitização server-side e CSP progressiva |
| MIME falso/upload malicioso | Comprometimento | Allowlist, detecção, nome aleatório, storage privado |
| Progresso enganoso | Decisões ruins | Pesos, cobertura e fórmula documentada |
| SQLite divergir do PostgreSQL | Falha de produção | CI PostgreSQL antes de deploy e ORM portável |
| Autosave sobrescrever edição | Perda de conteúdo | Versão otimista e histórico imutável |
| Deleção quebrar evidências | Perda histórica | `PROTECT`, arquivamento e purge separado |
| Dependência de CDN | UI offline/quebrada | Fixar versões; vendorizar assets antes de produção |
| Windows + servidor produtivo | Operação frágil | Waitress/IIS documentado; Linux/Nginx recomendado |

## 16. Critérios de aceite

### Fundação (esta entrega)

- Projeto inicia no Windows seguindo apenas o README.
- Configuração local usa `.env`; segredo não está versionado.
- Migração cria usuário personalizado antes de dados de domínio.
- O dashboard abre diretamente sem solicitar login ou senha.
- O primeiro acesso cria um único perfil pessoal com senha inutilizável.
- Rotas de login, logout e recuperação de senha não existem.
- Layout responde a desktop/mobile, menu recolhe e tema persiste.
- `python manage.py check`, migrations e testes passam.
- Configuração de produção falha de forma segura sem variáveis obrigatórias.

### MVP completo

Os 20 itens de aceite descritos no briefing são mantidos como checklist de
release. Além deles:

- Nenhuma rota ou arquivo permite acesso cruzado entre usuários.
- Regras críticas possuem testes automatizados.
- Operações essenciais funcionam sem JavaScript.
- O dashboard explica fórmula e cobertura do progresso.
- Upload inválido é recusado e arquivo válido não é público por URL direta.
