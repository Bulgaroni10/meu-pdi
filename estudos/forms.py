from django import forms

from objetivos.models import Objetivo

from .models import Aula, Curso, Disciplina, Periodo, Trilha


class FormPessoal(forms.ModelForm):
    def __init__(self, *args, usuario=None, **kwargs):
        self.usuario = usuario
        super().__init__(*args, **kwargs)
        if usuario is not None:
            self.instance.usuario = usuario


class TrilhaForm(FormPessoal):
    class Meta:
        model = Trilha
        exclude = ("usuario",)
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "prazo": forms.DateInput(attrs={"type": "date"}),
            "progresso": forms.NumberInput(attrs={"min": 0, "max": 100}),
            "prerequisitos": forms.Textarea(attrs={"rows": 2}),
            "observacoes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["objetivo"].queryset = Objetivo.objects.filter(
            usuario=self.usuario, arquivado_em__isnull=True
        )


class CursoForm(FormPessoal):
    class Meta:
        model = Curso
        exclude = ("usuario",)
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "data_prevista_conclusao": forms.DateInput(attrs={"type": "date"}),
            "data_real_conclusao": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["trilhas"].queryset = Trilha.objects.filter(usuario=self.usuario)


class PeriodoForm(FormPessoal):
    class Meta:
        model = Periodo
        exclude = ("usuario",)
        widgets = {
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "data_conclusao": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["curso"].queryset = Curso.objects.filter(usuario=self.usuario)


class DisciplinaForm(FormPessoal):
    class Meta:
        model = Disciplina
        exclude = ("usuario",)
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 2}),
            "ementa": forms.Textarea(attrs={"rows": 3}),
            "observacoes": forms.Textarea(attrs={"rows": 2}),
            "progresso": forms.NumberInput(attrs={"min": 0, "max": 100}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["curso"].queryset = Curso.objects.filter(usuario=self.usuario)
        self.fields["periodo"].queryset = Periodo.objects.filter(usuario=self.usuario)


class AulaForm(FormPessoal):
    class Meta:
        model = Aula
        exclude = ("usuario",)
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "descricao": forms.Textarea(attrs={"rows": 2}),
            "resumo": forms.Textarea(attrs={"rows": 3}),
            "duvidas": forms.Textarea(attrs={"rows": 3}),
            "aplicacao_pratica": forms.Textarea(attrs={"rows": 3}),
            "proxima_revisao": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["disciplina"].queryset = Disciplina.objects.filter(usuario=self.usuario)
