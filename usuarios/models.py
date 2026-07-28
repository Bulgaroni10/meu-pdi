from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import TimeStampedModel
from .managers import UsuarioManager


class Usuario(AbstractUser, TimeStampedModel):
    class Tema(models.TextChoices):
        SISTEMA = "sistema", "Usar tema do sistema"
        CLARO = "claro", "Claro"
        ESCURO = "escuro", "Escuro"

    username = None
    email = models.EmailField("e-mail", unique=True)
    nome = models.CharField("nome", max_length=150)
    cargo_atual = models.CharField("cargo atual", max_length=180, blank=True)
    cargo_desejado = models.CharField("cargo desejado", max_length=180, blank=True)
    resumo_profissional = models.TextField(
        "sobre mim",
        blank=True,
        help_text="Uma apresentação curta sobre sua experiência, interesses e direção profissional.",
    )
    objetivo_principal = models.TextField("objetivo principal", blank=True)
    localizacao = models.CharField("localização", max_length=120, blank=True)
    github_url = models.URLField("GitHub", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    timezone = models.CharField(
        "fuso horário", max_length=64, default="America/Sao_Paulo"
    )
    idioma = models.CharField("idioma", max_length=10, default="pt-br")
    tema = models.CharField(
        "tema", max_length=10, choices=Tema.choices, default=Tema.SISTEMA
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ("nome", "email")

    def __str__(self) -> str:
        return self.nome or self.email

    def save(self, *args, **kwargs):
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)

    def get_full_name(self) -> str:
        return self.nome

    def get_short_name(self) -> str:
        return self.nome.split()[0] if self.nome else self.email.split("@")[0]


class PreferenciaUsuario(TimeStampedModel):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="preferencias",
        primary_key=True,
    )
    menu_recolhido = models.BooleanField("menu recolhido", default=False)
    inicio_semana = models.PositiveSmallIntegerField(
        "início da semana",
        default=0,
        help_text="0 representa segunda-feira e 6 representa domingo.",
    )

    class Meta:
        verbose_name = "preferência do usuário"
        verbose_name_plural = "preferências dos usuários"

    def __str__(self) -> str:
        return f"Preferências de {self.usuario}"
