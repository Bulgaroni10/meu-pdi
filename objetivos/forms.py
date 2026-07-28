from django import forms

from .models import Objetivo


class ObjetivoForm(forms.ModelForm):
    tags_texto = forms.CharField(
        label="Tags",
        required=False,
        help_text="Separe as tags por vírgulas.",
        widget=forms.TextInput(attrs={"placeholder": "Ex.: Azure, carreira, 2027"}),
    )

    class Meta:
        model = Objetivo
        fields = (
            "titulo",
            "descricao",
            "categoria",
            "motivo",
            "data_inicio",
            "prazo",
            "prioridade",
            "status",
            "progresso",
            "resultado_esperado",
            "evidencia_esperada",
            "proxima_acao",
            "obstaculos",
            "observacoes",
        )
        widgets = {
            "titulo": forms.TextInput(
                attrs={"placeholder": "Ex.: Conquistar uma posição de nível pleno"}
            ),
            "descricao": forms.Textarea(attrs={"rows": 4}),
            "motivo": forms.Textarea(attrs={"rows": 3}),
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "prazo": forms.DateInput(attrs={"type": "date"}),
            "progresso": forms.NumberInput(
                attrs={"min": 0, "max": 100, "step": 5}
            ),
            "resultado_esperado": forms.Textarea(attrs={"rows": 3}),
            "evidencia_esperada": forms.Textarea(attrs={"rows": 3}),
            "proxima_acao": forms.TextInput(
                attrs={"placeholder": "A menor ação concreta que move este objetivo"}
            ),
            "obstaculos": forms.Textarea(attrs={"rows": 3}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            choice
            for choice in Objetivo.Status.choices
            if choice[0] != Objetivo.Status.ATRASADO
        ]
        if self.instance.pk:
            self.fields["tags_texto"].initial = ", ".join(
                self.instance.tags.values_list("nome", flat=True)
            )


class FiltroObjetivoForm(forms.Form):
    q = forms.CharField(
        label="Buscar",
        required=False,
        widget=forms.SearchInput(
            attrs={"placeholder": "Buscar por título, descrição ou próxima ação"}
        ),
    )
    status = forms.ChoiceField(
        label="Status",
        required=False,
        choices=[("", "Todos os status"), *Objetivo.Status.choices],
    )
    categoria = forms.ChoiceField(
        label="Categoria",
        required=False,
        choices=[("", "Todas as categorias"), *Objetivo.Categoria.choices],
    )
    prioridade = forms.ChoiceField(
        label="Prioridade",
        required=False,
        choices=[("", "Todas as prioridades"), *Objetivo.Prioridade.choices],
    )
    prazo = forms.ChoiceField(
        label="Prazo",
        required=False,
        choices=[
            ("", "Todos os prazos"),
            ("proximos_30", "Próximos 30 dias"),
            ("atrasados", "Atrasados"),
            ("sem_prazo", "Sem prazo"),
        ],
    )
    ordenacao = forms.ChoiceField(
        label="Ordenar",
        required=False,
        choices=[
            ("-updated_at", "Atualizados recentemente"),
            ("prazo", "Prazo mais próximo"),
            ("-prioridade", "Maior prioridade"),
            ("titulo", "Título de A a Z"),
            ("-progresso", "Maior progresso"),
        ],
    )
    arquivados = forms.BooleanField(label="Mostrar arquivados", required=False)
