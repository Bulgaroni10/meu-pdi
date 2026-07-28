from django import forms

from competencias.models import Competencia
from objetivos.models import Objetivo
from projetos.models import Projeto

from .models import AcaoRevisao, RevisaoPeriodica


class RevisaoForm(forms.ModelForm):
    class Meta:
        model = RevisaoPeriodica
        exclude = ("usuario", "status", "concluida_em")
        widgets = {
            "periodo_inicio": forms.DateInput(attrs={"type": "date"}),
            "periodo_fim": forms.DateInput(attrs={"type": "date"}),
            "nota_periodo": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "conquistas": forms.Textarea(attrs={"rows": 4}),
            "dificuldades": forms.Textarea(attrs={"rows": 4}),
            "aprendizados": forms.Textarea(attrs={"rows": 4}),
            "ajustes": forms.Textarea(attrs={"rows": 4}),
            "conclusao": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.usuario = usuario


class AcaoRevisaoForm(forms.ModelForm):
    class Meta:
        model = AcaoRevisao
        exclude = ("usuario", "revisao")
        widgets = {"prazo": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, usuario=None, revisao=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.usuario = usuario
        self.instance.revisao = revisao
        self.fields["objetivo"].queryset = Objetivo.objects.filter(
            usuario=usuario, arquivado_em__isnull=True
        )
        self.fields["projeto"].queryset = Projeto.objects.filter(
            usuario=usuario, arquivado_em__isnull=True
        )
        self.fields["competencia"].queryset = Competencia.objects.filter(
            usuario=usuario, arquivado_em__isnull=True
        )
