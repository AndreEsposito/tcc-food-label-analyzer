import re
import unicodedata


_CABECALHO_INGREDIENTES = re.compile(
    r"\b(?:lista\s+de\s+)?ingredientes?\s*[:\-]?",
    re.IGNORECASE,
)
_FIM_LISTA = re.compile(
    r"\b(?:alergicos?|alergênicos?|cont[eé]m\s+gl[uú]ten|não\s+cont[eé]m\s+gl[uú]ten|"
    r"informa(?:ção|cao)\s+nutricional|porção|porcao|validade|fabricado\s+por)\b",
    re.IGNORECASE,
)
_SINONIMOS_NORMALIZADOS = {
    r"\baromas artificiais\b": "aroma artificial",
    r"\baromas identicos aos naturais\b": "aroma identico ao natural",
    r"\bproteinas hidrolisadas\b": "proteina hidrolisada",
    r"\bproteinas lacteas\b": "proteina lactea",
    r"\bisolados proteicos\b": "isolado proteico",
    r"\boleos vegetais\b": "oleo vegetal",
    r"\bgorduras culinarias\b": "gordura culinaria",
    r"\bgordura vegetal interesterificada\b": "gordura interesterificada",
    r"\brealcadores de sabor\b": "realcador de sabor",
    r"\b(?:acessulfame|acesulfame) k\b": "acesulfame de potassio",
}


def preprocessar(texto: str) -> str:
    if not texto:
        return ""

    texto = texto.lower()

    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")

    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    for padrao, substituicao in _SINONIMOS_NORMALIZADOS.items():
        texto = re.sub(padrao, substituicao, texto)

    return texto


def extrair_trecho_ingredientes(texto: str) -> tuple[str, bool]:
    """Isola a lista quando o OCR preserva seu cabeçalho.

    Quando não há cabeçalho, mantém o texto completo para aceitar recortes que
    contenham somente a composição.
    """
    texto = (texto or "").strip()
    if not texto:
        return "", False

    cabecalho = _CABECALHO_INGREDIENTES.search(texto)
    trecho = texto[cabecalho.end() :] if cabecalho else texto
    fim = _FIM_LISTA.search(trecho)
    if fim:
        trecho = trecho[: fim.start()]
    return trecho.strip(" \t\r\n:;-"), cabecalho is not None


def separar_componentes(trecho: str) -> list[str]:
    """Separa componentes preservando frases compostas relevantes."""
    if not trecho:
        return []

    partes = re.split(r"[,;\n\r]+|\s+e\s+", trecho, flags=re.IGNORECASE)
    componentes: list[str] = []
    vistos: set[str] = set()
    for parte in partes:
        normalizada = preprocessar(parte)
        normalizada = re.sub(
            r"^(?:ingredientes?|composicao|produto)\s+", "", normalizada
        ).strip()
        if normalizada and normalizada not in vistos:
            vistos.add(normalizada)
            componentes.append(normalizada)
    return componentes
