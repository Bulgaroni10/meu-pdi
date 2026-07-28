import logging
import time
import uuid

from django.conf import settings
from django.http import JsonResponse


logger = logging.getLogger("meu_pdi.requests")


class RequestLogMiddleware:
    """Registra uma linha estruturada por requisição sem armazenar dados pessoais."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
        request.request_id = request_id[:64]
        inicio = time.perf_counter()
        response = self.get_response(request)
        duracao = round((time.perf_counter() - inicio) * 1000, 2)
        response["X-Request-ID"] = request.request_id
        logger.info(
            "request concluída",
            extra={
                "request_id": request.request_id,
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duracao,
                "event": "http_request",
            },
        )
        return response


class DemoSomenteLeituraMiddleware:
    """Impede alterações quando a versão pública de demonstração está ativa."""

    METODOS_SEGUROS = {"GET", "HEAD", "OPTIONS"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            settings.PUBLIC_DEMO_MODE
            and request.method not in self.METODOS_SEGUROS
        ):
            return JsonResponse(
                {
                    "detail": (
                        "Esta demonstração pública é somente leitura. "
                        "As alterações ficam disponíveis na instalação pessoal."
                    )
                },
                status=403,
            )
        return self.get_response(request)


class SecurityHeadersMiddleware:
    """Cabeçalhos defensivos compatíveis com a interface atual."""

    CSP = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.quilljs.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.quilljs.com; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "frame-src 'self'; connect-src 'self'; object-src 'none'; "
        "base-uri 'self'; form-action 'self'; frame-ancestors 'self'"
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Content-Security-Policy"] = self.CSP
        response["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
        )
        response["Cross-Origin-Opener-Policy"] = "same-origin"
        return response
