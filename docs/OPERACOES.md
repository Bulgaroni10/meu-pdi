# Operação, logs e monitoramento

## Sinais de saúde

| Endpoint | Finalidade | Dependências |
| --- | --- | --- |
| `/health/live/` | processo web está respondendo | aplicação |
| `/health/ready/` | instância pronta para receber tráfego | aplicação e banco |

O monitor da hospedagem consulta `/health/ready/`. Uma falha de banco retorna
HTTP 503 e impede que uma versão defeituosa receba tráfego.

## Logs

Em produção, `LOG_FORMAT=json` gera eventos como:

```json
{
  "timestamp": "2026-07-28T14:00:00+00:00",
  "level": "INFO",
  "logger": "meu_pdi.requests",
  "message": "request concluída",
  "request_id": "0c39...",
  "method": "GET",
  "path": "/indicadores/",
  "status_code": 200,
  "duration_ms": 42.7,
  "event": "http_request"
}
```

O mesmo identificador é devolvido em `X-Request-ID`, permitindo localizar uma
requisição específica. Query strings, corpo de formulários e conteúdo pessoal
não são registrados.

## Alertas recomendados

- disponibilidade abaixo de 99% por 5 minutos;
- `/health/ready/` retornando 5xx;
- taxa de respostas 5xx maior que 2% em 10 minutos;
- p95 de resposta acima de 1 segundo;
- erro novo no Sentry;
- uso de banco acima de 80%;
- falha ou ausência de backup.

## Sentry

Defina `SENTRY_DSN` na hospedagem. A integração é opcional e usa
`send_default_pii=False`. Ajuste `SENTRY_TRACES_SAMPLE_RATE` para controlar
volume e custo.

## Rotina operacional

### A cada deploy

1. executar testes e `check --deploy`;
2. aplicar migrations;
3. coletar arquivos estáticos;
4. confirmar `/health/live/` e `/health/ready/`;
5. navegar no dashboard e relatório;
6. revisar erros e tempo de resposta.

### Semanal

- verificar falhas e latência;
- conferir espaço e conexões do banco;
- confirmar atualização do backup.

### Mensal

- testar restauração;
- revisar dependências;
- conferir documentos e imagens da demonstração;
- revisar os indicadores apresentados.

## Recuperação

Os scripts `backup.ps1` e `restore.ps1` atendem o ambiente pessoal. Em produção,
usar os backups do PostgreSQL gerenciado. Antes de restaurar, interromper
escritas, preservar o banco atual e validar o resultado em ambiente separado.
