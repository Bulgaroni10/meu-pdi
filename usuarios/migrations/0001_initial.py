# Generated for Meu PDI foundation.

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import usuarios.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Usuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Designates that this user has all permissions without "
                            "explicitly assigning them."
                        ),
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(blank=True, max_length=150, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(blank=True, max_length=150, verbose_name="last name"),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "Designates whether this user should be treated as active. "
                            "Unselect this instead of deleting accounts."
                        ),
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="atualizado em")),
                (
                    "email",
                    models.EmailField(max_length=254, unique=True, verbose_name="e-mail"),
                ),
                ("nome", models.CharField(max_length=150, verbose_name="nome")),
                (
                    "cargo_atual",
                    models.CharField(blank=True, max_length=180, verbose_name="cargo atual"),
                ),
                (
                    "cargo_desejado",
                    models.CharField(blank=True, max_length=180, verbose_name="cargo desejado"),
                ),
                (
                    "objetivo_principal",
                    models.TextField(blank=True, verbose_name="objetivo principal"),
                ),
                (
                    "timezone",
                    models.CharField(
                        default="America/Sao_Paulo",
                        max_length=64,
                        verbose_name="fuso horário",
                    ),
                ),
                (
                    "idioma",
                    models.CharField(default="pt-br", max_length=10, verbose_name="idioma"),
                ),
                (
                    "tema",
                    models.CharField(
                        choices=[
                            ("sistema", "Usar tema do sistema"),
                            ("claro", "Claro"),
                            ("escuro", "Escuro"),
                        ],
                        default="sistema",
                        max_length=10,
                        verbose_name="tema",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text=(
                            "The groups this user belongs to. A user will get all "
                            "permissions granted to each of their groups."
                        ),
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "usuário",
                "verbose_name_plural": "usuários",
                "ordering": ("nome", "email"),
            },
            managers=[("objects", usuarios.managers.UsuarioManager())],
        ),
        migrations.CreateModel(
            name="PreferenciaUsuario",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="criado em"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="atualizado em"),
                ),
                (
                    "menu_recolhido",
                    models.BooleanField(default=False, verbose_name="menu recolhido"),
                ),
                (
                    "inicio_semana",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="0 representa segunda-feira e 6 representa domingo.",
                        verbose_name="início da semana",
                    ),
                ),
                (
                    "usuario",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="preferencias",
                        serialize=False,
                        to="usuarios.usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "preferência do usuário",
                "verbose_name_plural": "preferências dos usuários",
            },
        ),
    ]
