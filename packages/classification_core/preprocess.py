import re
import unicodedata


_CABECALHO_INGREDIENTES = re.compile(
    r"\b(?:lista\s+de\s+)?(?:ingredientes?|ingredients|ingr\.)(?:\s+(?:do|de)\s+(?:macarr[ãa]o|tempero\s+em\s+p[óo]))?\s*[:\-]?",
    re.IGNORECASE,
)
_FIM_LISTA = re.compile(
    r"\b(?:al[eé]rgicos?|alerg[eê]nicos?|cont[eé]m\s+gl[uú]ten|n[ãa]o\s+cont[eé]m\s+gl[uú]ten|"
    r"(?:n[ãa]o\s+)?cont[eé]m\s+lactose|gluten\s+free|allergen\s+warning|"
    r"informa(?:ção|cao)\s+nutricional|valores\s+nutricionais|porção|porcao|"
    r"validade|fabricado\s+por|conservar\s+em|mantenha\s+em|"
    r"modo\s+de\s+preparo|sugest[ãa]o\s+de\s+preparo)\b",
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
    r"\bextra virgem\b": "extravirgem",
    r"\bsardinhas\b": "sardinha",
    r"\bfermentos lacteos\b": "fermento lacteo",
    r"\baromas naturais\b": "aroma natural",
    r"\bcreatine monohydrate\b": "creatina monohidratada",
    r"\be 150\s*d\b": "e150d",
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
    # Inclui sublistas do mesmo produto, como massa e tempero do macarrão.
    trecho = _CABECALHO_INGREDIENTES.sub(" ", trecho)
    return trecho.strip(" \t\r\n:;-"), cabecalho is not None


def separar_componentes(trecho: str) -> list[str]:
    """Separa componentes preservando frases compostas relevantes."""
    if not trecho:
        return []

    partes = re.split(r"[,;\n\r]+|(?<!mono)\s+e\s+", trecho, flags=re.IGNORECASE)
    componentes: list[str] = []
    vistos: set[str] = set()
    for parte in partes:
        parte = re.sub(r"^\s*100\s*%\s*(?=azeite\b)", "", parte, flags=re.IGNORECASE)
        normalizada = preprocessar(parte)
        normalizada = re.sub(
            r"^(?:ingredientes?|composicao|produto)\s+", "", normalizada
        ).strip()
        if normalizada and normalizada not in vistos:
            vistos.add(normalizada)
            componentes.append(normalizada)
    return componentes
