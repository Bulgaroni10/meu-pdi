from django import forms

from projetos.models import Evidencia

from .models import AvaliacaoCompetencia, Competencia


class CompetenciaForm(forms.ModelForm):
    class Meta:
        model = Competencia
        exclude = ("usuario", "arquivado_em")
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "nivel_desejado": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "criterios": forms.Textarea(attrs={"rows": 4}),
            "prazo": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.usuario = usuario


class AvaliacaoForm(forms.ModelForm):
    evidencias = forms.ModelMultipleChoiceField(
        queryset=Evidencia.objects.none(),
        label="Evidências que comprovam este nível",
        help_text="Selecione ao menos uma evidência registrada em Projetos.",
    )

    class Meta:
        model = AvaliacaoCompetencia
        fields = ("nivel", "justificativa", "data", "evidencias")
        widgets = {
            "nivel": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "justificativa": forms.Textarea(attrs={"rows": 5}),
            "data": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["evidencias"].queryset = Evidencia.objects.filter(
            usuario=usuario
        ).select_related("projeto")
