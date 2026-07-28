# Checklist de produção

## Segredos e configuração

- [ ] `DJANGO_SETTINGS_MODULE=config.settings.production`.
- [ ] `DJANGO_SECRET_KEY` aleatória, longa e armazenada em cofre.
- [ ] `DEBUG=False` confirmado.
- [ ] `DJANGO_ALLOWED_HOSTS` contém somente domínios reais.
- [ ] `DJANGO_CSRF_TRUSTED_ORIGINS` contém origens HTTPS reais.
- [ ] `.env`, backups e uploads estão fora do Git.

## Banco

- [ ] PostgreSQL com usuário exclusivo e privilégio mínimo.
- [ ] Conexão criptografada quando banco e aplicação estão em hosts diferentes.
- [ ] Migrations testadas em cópia do ambiente.
- [ ] Backup automatizado, criptografado e com retenção definida.
- [ ] Restauração testada e tempo de recuperação registrado.

## HTTP e processo

- [ ] TLS válido e renovação automatizada.
- [ ] Proxy envia `X-Forwarded-Proto`.
- [ ] Waitress/Gunicorn executa com conta sem privilégios administrativos.
- [ ] Aplicação escuta apenas na interface privada.
- [ ] Limites de requisição configurados também no proxy.
- [ ] Logs têm rotação e não armazenam segredos.

## Django

- [ ] `python manage.py check --deploy` sem alertas.
- [ ] `python manage.py test` aprovado.
- [ ] `python manage.py collectstatic --noinput` concluído.
- [ ] HSTS ativado somente após confirmar HTTPS em todos os subdomínios.
- [ ] Modo pessoal sem senha não está exposto fora de `127.0.0.1`.
- [ ] `PDI_REQUIRE_LOGIN=true` confirmado na instalação pessoal editável.
- [ ] `PDI_ADMIN_EMAIL` e `PDI_ADMIN_PASSWORD` configurados como segredos.
- [ ] `PUBLIC_DEMO_MODE=false` confirmado na instalação pessoal editável.
- [ ] Tentativas de POST na demonstração retornam HTTP 403.

## Uploads e biblioteca

- [ ] Storage privado fora da raiz pública.
- [ ] Extensão, MIME, assinatura e tamanho validados.
- [ ] Nomes aleatórios e `Content-Disposition` seguro.
- [ ] Antivírus ou sandbox de upload definido.
- [ ] URLs temporárias ou view autorizada testadas contra IDOR.

Para o uso pessoal local, a rota direta `/media/` permanece desativada e os
PDFs são entregues somente pelas views protegidas.

## Operação

- [ ] Monitoramento de disponibilidade, erro e espaço em disco.
- [ ] `/health/live/` e `/health/ready/` monitorados.
- [ ] Logs JSON e `X-Request-ID` confirmados após o primeiro acesso.
- [ ] Sentry configurado sem coleta padrão de PII, quando utilizado.
- [ ] Alertas possuem responsável e procedimento.
- [ ] Plano de rollback da aplicação e migrations.
- [ ] Política de atualização mensal de dependências.
- [ ] Conta break-glass protegida e auditada.
