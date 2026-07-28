import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class ErroLeituraPDF(ValueError):
    pass


@dataclass(frozen=True)
class SecaoPDF:
    titulo: str
    conteudo: str


@dataclass(frozen=True)
class DocumentoExtraido:
    titulo: str
    paginas: int
    texto: str
    secoes: list[SecaoPDF]


PADRAO_TITULO = re.compile(
    r"^(?:"
    r"(?:fase|etapa|cap[ií]tulo|m[oó]dulo|unidade|parte|se[cç][aã]o|semana|aula)"
    r"\s*[0-9ivx]*"
    r"|\d+(?:\.\d+)*[\s\-:.)]+"
    r")",
    re.IGNORECASE,
)


def _limpar_linha(linha: str) -> str:
    return re.sub(r"\s+", " ", linha).strip(" \t-–—")


def _parece_titulo(linha: str) -> bool:
    if not 4 <= len(linha) <= 110 or linha.endswith((".", ";", ",")):
        return False
    palavras = linha.split()
    if len(palavras) > 14:
        return False
    if PADRAO_TITULO.match(linha):
        return True
    letras = [char for char in linha if char.isalpha()]
    return bool(letras) and sum(char.isupper() for char in letras) / len(letras) >= 0.82


def _titulo_resumido(texto: str, indice: int) -> str:
    primeira = re.split(r"(?<=[.!?])\s+", texto.strip())[0]
    palavras = primeira.split()[:9]
    titulo = " ".join(palavras).strip(" .,:;-")
    return titulo[:100] if len(titulo) >= 4 else f"Etapa {indice}"


def identificar_secoes(texto: str) -> list[SecaoPDF]:
    linhas = [_limpar_linha(linha) for linha in texto.splitlines()]
    linhas = [linha for linha in linhas if linha]
    secoes: list[SecaoPDF] = []
    titulo_atual = ""
    conteudo_atual: list[str] = []
    titulos_vistos: set[str] = set()

    def salvar():
        if not titulo_atual:
            return
        conteudo = " ".join(conteudo_atual).strip()
        if conteudo or not secoes:
            secoes.append(SecaoPDF(titulo=titulo_atual, conteudo=conteudo))

    for linha in linhas:
        if _parece_titulo(linha):
            chave = re.sub(r"\W+", "", linha.casefold())
            if chave in titulos_vistos:
                continue
            if titulo_atual:
                salvar()
            titulo_atual = linha[:180]
            conteudo_atual = []
            titulos_vistos.add(chave)
        elif titulo_atual:
            conteudo_atual.append(linha)

    salvar()
    secoes = [secao for secao in secoes if secao.conteudo]
    if len(secoes) >= 2:
        return secoes[:12]

    paragrafos = [
        re.sub(r"\s+", " ", bloco).strip()
        for bloco in re.split(r"\n\s*\n", texto)
        if len(re.sub(r"\s+", " ", bloco).strip()) >= 80
    ]
    if not paragrafos:
        paragrafos = [
            " ".join(linhas[indice : indice + 12])
            for indice in range(0, len(linhas), 12)
        ]
    secoes_fallback = []
    for indice, bloco in enumerate(paragrafos[:8], start=1):
        secoes_fallback.append(
            SecaoPDF(
                titulo=_titulo_resumido(bloco, indice),
                conteudo=bloco[:3000],
            )
        )
    return secoes_fallback


def extrair_pdf(arquivo) -> DocumentoExtraido:
    try:
        reader = PdfReader(arquivo)
        if reader.is_encrypted and reader.decrypt("") == 0:
            raise ErroLeituraPDF("O PDF está protegido por senha.")
        if len(reader.pages) > 250:
            raise ErroLeituraPDF("O PDF possui mais de 250 páginas.")
        textos = []
        for pagina in reader.pages:
            textos.append(pagina.extract_text() or "")
    except ErroLeituraPDF:
        raise
    except (PdfReadError, OSError, ValueError) as exc:
        raise ErroLeituraPDF("Não foi possível ler este PDF.") from exc
    finally:
        arquivo.seek(0)

    texto = "\n\n".join(textos)
    texto = texto.replace("\x00", "").strip()
    if len(re.sub(r"\s+", "", texto)) < 80:
        raise ErroLeituraPDF(
            "O PDF não possui texto suficiente. PDFs digitalizados precisam de OCR."
        )
    texto = texto[:250_000]
    metadados = reader.metadata or {}
    titulo = str(metadados.get("/Title") or "").strip()
    if not titulo:
        titulo = Path(getattr(arquivo, "name", "Roadmap")).stem
    secoes = identificar_secoes(texto)
    if not secoes:
        raise ErroLeituraPDF("Não foi possível identificar tópicos no PDF.")
    return DocumentoExtraido(
        titulo=titulo[:180],
        paginas=len(reader.pages),
        texto=texto,
        secoes=secoes,
    )
