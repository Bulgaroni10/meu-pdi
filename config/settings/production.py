"""Configurações seguras para produção."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
import dj_database_url

required = {
    "DJANGO_SECRET_KEY": os.getenv("DJANGO_SECRET_KEY"),  # noqa: F405
}
missing = [name for name, value in required.items() if not value]
if missing:
    raise ImproperlyConfigured(
        f"Variáveis obrigatórias ausentes: {', '.join(missing)}"
    )

DEBUG = False
SECRET_KEY = required["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")  # noqa: F405
if render_hostname := os.getenv("RENDER_EXTERNAL_HOSTNAME"):  # noqa: F405
    ALLOWED_HOSTS.append(render_hostname)
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_hostname}")  # noqa: F405
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "Defina DJANGO_ALLOWED_HOSTS ou RENDER_EXTERNAL_HOSTNAME."
    )

if database_url := os.getenv("DATABASE_URL"):  # noqa: F405
    DATABASES["default"] = dj_database_url.config(  # noqa: F405
        default=database_url,
        conn_max_age=int(os.getenv("DB_CONN_MAX_AGE", "60")),  # noqa: F405
        conn_health_checks=True,
        ssl_require=not env_bool("DB_SSL_DISABLE", False),  # noqa: F405
    )

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if sentry_dsn := os.getenv("SENTRY_DSN"):  # noqa: F405
    import sentry_sdk

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=os.getenv("APP_ENVIRONMENT", "production"),  # noqa: F405
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),  # noqa: F405
        send_default_pii=False,
    )
