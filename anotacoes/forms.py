from django import forms

from estudos.models import Aula
from .models import Anotacao


class AnotacaoForm(forms.ModelForm):
    class Meta:
        model = Anotacao
        fields = (
            "aula", "titulo", "tipo", "pagina_pdf", "trecho_referencia",
            "favorita", "tags", "conteudo_html",
        )
        widgets = {
            "conteudo_html": forms.HiddenInput(),
            "trecho_referencia": forms.Textarea(attrs={"rows": 2}),
            "pagina_pdf": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.usuario = usuario
        self.fields["aula"].queryset = Aula.objects.filter(usuario=usuario)
