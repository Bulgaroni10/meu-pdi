from django import forms
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm,
)

from .models import Usuario


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = (
            "nome",
            "email",
            "cargo_atual",
            "cargo_desejado",
            "resumo_profissional",
            "objetivo_principal",
            "localizacao",
            "github_url",
            "linkedin_url",
            "timezone",
            "idioma",
            "tema",
        )
        widgets = {
            "resumo_profissional": forms.Textarea(attrs={"rows": 4}),
            "objetivo_principal": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        conflito = Usuario.objects.exclude(pk=self.instance.pk).filter(email=email)
        if conflito.exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email


class UsuarioAdminCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("email", "nome")


class UsuarioAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = "__all__"
