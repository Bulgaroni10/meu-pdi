# Segurança

## Modelo de exposição

Existem três modos deliberadamente separados:

- **pessoal local:** sem login, editável, restrito ao computador do proprietário;
- **pessoal publicado:** login obrigatório, editável e acessível por dispositivos
  autorizados;
- **demonstração pública:** sem login e estritamente somente leitura.

O middleware `UsuarioPessoalMiddleware` exige autenticação quando
`PDI_REQUIRE_LOGIN=true`. Apenas `/conta/login/`, `/health/live/` e
`/health/ready/` permanecem públicos.

O middleware `DemoSomenteLeituraMiddleware` bloqueia métodos diferentes de GET,
HEAD e OPTIONS quando `PUBLIC_DEMO_MODE=true`. A versão pública deve conter
somente dados demonstrativos.

## Ameaças e controles

| Ameaça | Controle |
| --- | --- |
| Acesso aos dados pessoais | Login obrigatório na implantação editável |
| Sequestro de sessão | HTTPS, cookies Secure, HttpOnly e SameSite |
| Senha exposta no repositório | Credencial fornecida por segredo de ambiente |
| Alteração pública sem autenticação | Demo pública somente leitura |
| Acesso direto a uploads | Ausência de rota pública para `/media/`; views protegidas |
| Upload disfarçado | Validação de assinatura, extensão, MIME, páginas e tamanho |
| Injeção de HTML nas anotações | Sanitização com lista permitida |
| CSRF | Middleware e token em formulários |
| Clickjacking | `X-Frame-Options` e CSP `frame-ancestors` |
| MIME sniffing | `X-Content-Type-Options: nosniff` |
| Conteúdo externo malicioso | Content Security Policy |
| Vazamento de segredos | Configuração por variáveis e `.env` ignorado |
| Host header | `ALLOWED_HOSTS` explícito |
| Tráfego sem criptografia | Redirect HTTPS, cookies Secure e HSTS |
| Exclusão acidental | Confirmação, POST e `PROTECT` em histórico relacionado |
| Exposição em logs | Logs registram rota e desempenho, não conteúdo ou parâmetros |

## Cabeçalhos

A produção ativa HSTS, HTTPS obrigatório, cookies seguros, proteção de
referência, CSP, Permissions Policy, COOP e proteção contra framing. A CSP ainda
permite scripts e estilos inline porque a interface legada os utiliza; remover
essa exceção é uma melhoria futura.

## Dados e privacidade

- não usar dados corporativos, credenciais ou documentos confidenciais na demo;
- manter uploads fora do Git;
- usar PostgreSQL gerenciado com credenciais exclusivas;
- fazer backup e testar restauração;
- configurar `send_default_pii=False` no Sentry;
- rotacionar chaves se houver suspeita de exposição.

## Verificação

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings.production"
$env:DJANGO_SECRET_KEY="uma-chave-com-mais-de-50-caracteres-e-alta-entropia"
$env:DJANGO_ALLOWED_HOSTS="localhost"
.\.venv\Scripts\python.exe manage.py check --deploy
```

Dependências são verificadas pelo Dependabot e os testes de segurança essenciais
fazem parte do pipeline.

## Limites conhecidos

A instalação é pessoal e não oferece cadastro público nem múltiplas contas.
Recuperação automática por e-mail não está habilitada; em caso de perda de
acesso, a credencial deve ser recuperada pelo ambiente seguro da hospedagem. O
modo local sem login não deve ser exposto na rede.
