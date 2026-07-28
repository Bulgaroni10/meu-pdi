# Segurança

## Modelo de exposição

Existem dois modos deliberadamente separados:

- **pessoal local:** sem login, editável, restrito ao computador do proprietário;
- **demonstração pública:** sem login e estritamente somente leitura.

O middleware `DemoSomenteLeituraMiddleware` bloqueia métodos diferentes de GET,
HEAD e OPTIONS quando `PUBLIC_DEMO_MODE=true`. A versão pública deve conter
somente dados demonstrativos.

## Ameaças e controles

| Ameaça | Controle |
| --- | --- |
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

A instalação pessoal não possui autenticação e não deve ser publicada em modo
editável. A demonstração não é um sistema multiusuário. Para oferecer edição
pela internet, o próximo passo obrigatório é autenticação, autorização por
objeto, recuperação de conta e gestão segura de sessão.
