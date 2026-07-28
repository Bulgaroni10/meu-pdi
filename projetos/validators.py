from django.core.exceptions import ValidationError


LIMITE_IMAGEM = 8 * 1024 * 1024


def validar_imagem_evidencia(arquivo):
    if arquivo.size > LIMITE_IMAGEM:
        raise ValidationError("A imagem deve ter no máximo 8 MB.")

    posicao = arquivo.tell()
    cabecalho = arquivo.read(16)
    arquivo.seek(posicao)
    eh_png = cabecalho.startswith(b"\x89PNG\r\n\x1a\n")
    eh_jpeg = cabecalho.startswith(b"\xff\xd8\xff")
    eh_webp = cabecalho.startswith(b"RIFF") and cabecalho[8:12] == b"WEBP"
    if not (eh_png or eh_jpeg or eh_webp):
        raise ValidationError("Envie uma imagem PNG, JPG ou WebP válida.")
