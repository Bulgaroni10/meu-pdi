import json
import logging
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Formato estruturado para busca e correlação em plataformas de logs."""

    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for campo in (
            "request_id",
            "method",
            "path",
            "status_code",
            "duration_ms",
            "event",
        ):
            valor = getattr(record, campo, None)
            if valor is not None:
                payload[campo] = valor
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)
