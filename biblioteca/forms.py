from pathlib import Path

from django import forms
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from estudos.models import Aula
from .models import MaterialPDF


class MaterialPDFForm(forms.ModelForm):
    class Meta:
        model = MaterialPDF
        fields = ("aula", "titulo", "descricao", "arquivo", "principal")
        widgets = {"descricao": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, usuario=None, **kwargs):
        self.usuario = usuario
        super().__init__(*args, **kwargs)
        self.instance.usuario = usuario
        self.fields["aula"].queryset = Aula.objects.filter(usuario=usuario).select_related(
            "disciplina"
        )
        self.fields["arquivo"].widget.attrs.update(
            {"accept": "application/pdf,.pdf"}
        )

    def clean_arquivo(self):
        arquivo = self.cleaned_data["arquivo"]
        if arquivo.size > 20 * 1024 * 1024:
            raise forms.ValidationError("O PDF deve ter no máximo 20 MB.")
        if Path(arquivo.name).suffix.lower() != ".pdf":
            raise forms.ValidationError("Envie um arquivo com extensão .pdf.")
        if arquivo.content_type not in {"application/pdf", "application/x-pdf"}:
            raise forms.ValidationError("O tipo do arquivo não é um PDF válido.")
        if arquivo.read(5) != b"%PDF-":
            arquivo.seek(0)
            raise forms.ValidationError("A assinatura do PDF é inválida.")
        arquivo.seek(0)
        try:
            reader = PdfReader(arquivo)
            if reader.is_encrypted and reader.decrypt("") == 0:
                raise forms.ValidationError("PDF protegido por senha não é suportado.")
            self.quantidade_paginas = len(reader.pages)
        except PdfReadError as exc:
            raise forms.ValidationError("Não foi possível ler este PDF.") from exc
        finally:
            arquivo.seek(0)
        return arquivo
