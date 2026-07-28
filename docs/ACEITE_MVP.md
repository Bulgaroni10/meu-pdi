# Aceite final do MVP pessoal

Data da revisão: 28/07/2026

## Resultado

O Meu PDI está apto para uso pessoal local no endereço
`http://127.0.0.1:8000`. O sistema não possui login ou senha e, por isso, deve
continuar restrito ao próprio computador.

## Escopo validado

- acesso direto e perfil pessoal único;
- objetivos, prazos, progresso, tags e histórico;
- geração de roadmap a partir de PDF com texto selecionável;
- trilhas, cursos, períodos, disciplinas e aulas;
- biblioteca privada de PDFs;
- anotações ricas, autosave e versões;
- projetos, tarefas, marcos, tecnologias e evidências;
- competências avaliadas por evidências;
- revisões periódicas e próximas ações;
- certificações, provas, custos e resultados;
- busca global;
- dashboard e indicadores consolidados;
- tema claro/escuro, menu recolhível e navegação móvel.

## Segurança verificada

- todos os dados de domínio são filtrados pelo proprietário interno;
- testes adversariais confirmam resposta 404 para registros de outro perfil;
- uploads validam extensão, MIME, assinatura, tamanho e leitura do PDF;
- nomes físicos dos uploads são aleatórios;
- arquivos não são publicados pela rota direta `/media/`;
- PDFs são entregues apenas por views protegidas, sem cache compartilhado;
- o visualizador interno usa `SAMEORIGIN`; as demais páginas permanecem com
  proteção de frame `DENY`;
- mutações usam POST e proteção CSRF;
- HTML das anotações é sanitizado no servidor;
- a configuração de produção exige segredo e hosts explícitos;
- `manage.py check --deploy` passa com a configuração segura de auditoria.

## Responsividade e usabilidade

Foram verificados o Dashboard, Indicadores, Projetos, Competências, Revisões,
Certificações, Busca e Aulas em desktop e em largura de celular. Não foi
identificada rolagem horizontal após os ajustes finais. Também foram validados:

- menu móvel e bloqueio do conteúdo enquanto aberto;
- busca acessível na barra superior e atalho `/`;
- hierarquia de títulos e ações com nomes acessíveis;
- estados vazios e mensagens de confirmação;
- funcionamento em tema claro e escuro.

## Limitações conhecidas

- Bootstrap, Bootstrap Icons, HTMX e Quill são carregados por CDN; a interface
  rica requer internet para carregar esses recursos pela primeira vez.
- PDFs digitalizados somente como imagem ainda não possuem OCR.
- O visualizador de PDF usa o leitor nativo do navegador.
- Não há antivírus para uploads; os arquivos devem ser documentos pessoais de
  origem conhecida.
- SQLite é adequado ao uso pessoal local. PostgreSQL continua sendo a opção
  documentada para uma implantação futura.
- O modo sem senha não deve ser publicado na internet nem aberto para a rede
  local.

## Operação recomendada

1. Iniciar pelo arquivo `iniciar.cmd`.
2. Manter o endereço em `127.0.0.1`.
3. Executar backup periódico com `scripts/backup.ps1`.
4. Manter uma cópia separada da pasta `media/`.
5. Atualizar dependências e repetir os testes periodicamente.
