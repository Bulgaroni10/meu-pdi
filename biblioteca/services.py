import hashlib

from django.db import transaction

from .models import MaterialPDF


@transaction.atomic
def salvar_pdf(form, usuario):
    arquivo = form.cleaned_data["arquivo"]
    digest = hashlib.sha256(arquivo.read()).hexdigest()
    arquivo.seek(0)
    material = form.save(commit=False)
    material.usuario = usuario
    material.nome_original = arquivo.name[:255]
    material.tamanho = arquivo.size
    material.sha256 = digest
    material.quantidade_paginas = form.quantidade_paginas
    if material.principal:
        MaterialPDF.objects.filter(
            usuario=usuario, aula=material.aula, principal=True
        ).update(principal=False)
    material.full_clean()
    material.save()
    return material
