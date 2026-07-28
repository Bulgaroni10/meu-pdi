from django import forms

from biblioteca.models import MaterialPDF
from objetivos.models import Objetivo

from .models import Evidencia, MarcoProjeto, Projeto, TarefaProjeto, Tecnologia


class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        exclude = ("usuario", "data_conclusao", "arquivado_em")
        widgets = {
            "problema": forms.Textarea(attrs={"rows": 3}),
            "solucao": forms.Textarea(attrs={"rows": 3}),
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "prazo": forms.DateInput(attrs={"type": "date"}),
            "progresso": forms.NumberInput(attrs={"min": 0, "max": 100}),
            "resultado": forms.Textarea(attrs={"rows": 3}),
            "aprendizados": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        self.instance.usuario = usuario
        self.fields["objetivo"].queryset = Objetivo.objects.filter(
            usuario=usuario, arquivado_em__isnull=True
        )


class MarcoForm(forms.ModelForm):
    class Meta:
        model = MarcoProjeto
        exclude = ("usuario", "projeto", "ordem")
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "prazo": forms.DateInput(attrs={"type": "date"}),
        }


class TarefaForm(forms.ModelForm):
    class Meta:
        model = TarefaProjeto
        exclude = ("usuario", "projeto", "ordem")
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "prazo": forms.DateInput(attrs={"type": "date"}),
        }


class TecnologiaForm(forms.Form):
    nome = forms.CharField(max_length=80, label="Tecnologia")
    categoria = forms.ChoiceField(choices=Tecnologia.Categoria.choices)


class EvidenciaForm(forms.ModelForm):
    class Meta:
        model = Evidencia
        exclude = ("usuario", "projeto")
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 4}),
            "data": forms.DateInput(attrs={"type": "date"}),
            "imagem": forms.FileInput(
                attrs={"accept": "image/png,image/jpeg,image/webp"}
            ),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["material"].queryset = MaterialPDF.objects.filter(usuario=usuario)
