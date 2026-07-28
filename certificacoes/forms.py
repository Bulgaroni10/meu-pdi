from django import forms

from biblioteca.models import MaterialPDF
from estudos.models import Trilha
from objetivos.models import Objetivo

from .models import Certificacao


class CertificacaoForm(forms.ModelForm):
    class Meta:
        model = Certificacao
        exclude = ("usuario", "arquivado_em")
        widgets = {
            "progresso": forms.NumberInput(attrs={"min": 0, "max": 100}),
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "data_prova": forms.DateInput(attrs={"type": "date"}),
            "data_resultado": forms.DateInput(attrs={"type": "date"}),
            "data_validade": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.usuario = usuario
        self.fields["objetivo"].queryset = Objetivo.objects.filter(
            usuario=usuario, arquivado_em__isnull=True
        )
        self.fields["trilha"].queryset = Trilha.objects.filter(usuario=usuario)
        self.fields["certificado"].queryset = MaterialPDF.objects.filter(usuario=usuario)
