from pathlib import Path

from django import forms

from objetivos.models import Objetivo


class ImportarRoadmapPDFForm(forms.Form):
    pdf = forms.FileField(
        label="Arquivo PDF",
        help_text="PDF com texto selecionável, até 15 MB e 250 páginas.",
        widget=forms.ClearableFileInput(attrs={"accept": "application/pdf,.pdf"}),
    )
    nome = forms.CharField(
        label="Nome do roadmap",
        required=False,
        max_length=180,
        help_text="Se ficar vazio, o sistema usará o título ou nome do PDF.",
    )
    objetivo = forms.ModelChoiceField(
        label="Objetivo relacionado",
        queryset=Objetivo.objects.none(),
        required=False,
        empty_label="Nenhum objetivo relacionado",
    )

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario is not None:
            self.fields["objetivo"].queryset = Objetivo.objects.filter(
                usuario=usuario,
                arquivado_em__isnull=True,
            )

    def clean_pdf(self):
        arquivo = self.cleaned_data["pdf"]
        if arquivo.size > 15 * 1024 * 1024:
            raise forms.ValidationError("O PDF deve ter no máximo 15 MB.")
        if Path(arquivo.name).suffix.lower() != ".pdf":
            raise forms.ValidationError("Envie um arquivo com extensão .pdf.")
        if arquivo.content_type not in {"application/pdf", "application/x-pdf"}:
            raise forms.ValidationError("O tipo do arquivo não é um PDF válido.")
        cabecalho = arquivo.read(5)
        arquivo.seek(0)
        if cabecalho != b"%PDF-":
            raise forms.ValidationError("A assinatura do arquivo PDF é inválida.")
        return arquivo
