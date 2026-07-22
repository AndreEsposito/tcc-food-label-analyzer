import re

from .preprocess import extrair_trecho_ingredientes, preprocessar, separar_componentes


MARCADORES_GRUPO_4: dict[str, tuple[str, str]] = {
    "aromatizante": ("aromatizante", "Substância usada para conferir ou intensificar aroma e sabor."),
    "aroma artificial": ("aromatizante", "Aroma formulado industrialmente para modificar o sabor."),
    "aroma identico ao natural": ("aromatizante", "Aroma formulado para reproduzir um aroma natural."),
    "corante": ("corante", "Substância usada para alterar ou reforçar a cor do produto."),
    "caramelo iv": ("corante", "Corante caramelo classe IV usado em formulações industriais."),
    "ins 150d": ("corante", "Código INS do corante caramelo classe IV."),
    "ins 150 d": ("corante", "Código INS do corante caramelo classe IV."),
    "glutamato monossodico": ("realçador de sabor", "Realçador usado para intensificar o sabor."),
    "realcador de sabor": ("realçador de sabor", "Aditivo usado para intensificar o sabor."),
    "maltodextrina": ("ingrediente industrial", "Carboidrato processado frequente em formulações industriais."),
    "xarope de glicose frutose": ("açúcar industrial", "Xarope industrial composto por glicose e frutose."),
    "xarope de glicose": ("açúcar industrial", "Xarope concentrado usado em formulações industriais."),
    "xarope de milho": ("açúcar industrial", "Xarope derivado do milho usado em formulações industriais."),
    "acucar invertido": ("açúcar industrial", "Açúcar transformado para uso em formulações industriais."),
    "solidos de xarope": ("açúcar industrial", "Ingrediente derivado de xarope concentrado."),
    "edulcorante": ("edulcorante", "Substância usada para adoçar o produto."),
    "aspartame": ("edulcorante", "Edulcorante artificial usado para adoçar o produto."),
    "sucralose": ("edulcorante", "Edulcorante usado para adoçar o produto."),
    "acesulfame de potassio": ("edulcorante", "Edulcorante artificial usado para adoçar o produto."),
    "ciclamato": ("edulcorante", "Edulcorante artificial usado para adoçar o produto."),
    "sacarina": ("edulcorante", "Edulcorante artificial usado para adoçar o produto."),
    "gordura vegetal hidrogenada": ("gordura modificada", "Gordura modificada por processo industrial."),
    "gordura interesterificada": ("gordura modificada", "Gordura rearranjada por processo industrial."),
    "amido modificado": ("ingrediente industrial", "Amido alterado para modificar textura ou estabilidade."),
    "proteina hidrolisada": ("ingrediente industrial", "Proteína processada por hidrólise para uso na formulação."),
    "extrato de levedura": ("realçador de sabor", "Ingrediente usado para intensificar características de sabor."),
    "isolado proteico": ("ingrediente industrial", "Fração proteica isolada por processamento industrial."),
    "caseinato": ("ingrediente industrial", "Derivado proteico do leite usado em formulações industriais."),
    "polidextrose": ("ingrediente industrial", "Polímero de glicose usado para modificar corpo e composição."),
    "carboximetilcelulose": ("espessante", "Aditivo usado para modificar textura e estabilidade."),
    "carboximetil celulose": ("espessante", "Aditivo usado para modificar textura e estabilidade."),
    "mono e diglicerideos de acidos graxos": ("emulsificante", "Emulsificante usado para estabilizar misturas industriais."),
    "monoglicerideos de acidos graxos": ("emulsificante", "Emulsificante usado para estabilizar misturas industriais."),
    "diglicerideos de acidos graxos": ("emulsificante", "Emulsificante usado para estabilizar misturas industriais."),
}

FAMILIAS_GRUPO_2: dict[str, tuple[str, ...]] = {
    "acucar": (
        "acucar", "acucar refinado", "acucar cristal", "acucar demerara",
        "acucar mascavo", "sacarose de cana de acucar",
    ),
    "sal": ("sal", "sal refinado", "sal marinho", "cloreto de sodio"),
    "oleo": ("oleo vegetal", "oleo de soja", "oleo de girassol", "oleo de milho", "oleo de canola"),
    "azeite": (
        "azeite", "azeite de oliva", "azeite de oliva extravirgem",
        "azeite extravirgem", "azeite de oliva refinado", "azeite de oliva virgem",
    ),
    "manteiga": ("manteiga",),
    "gordura": ("banha", "banha suina", "gordura suina", "gordura culinaria"),
}

AUXILIARES_GRUPO_2: dict[str, tuple[str, ...]] = {
    "sal": ("iodato de potassio", "dioxido de silicio", "antiumectante", "ferrocianeto de sodio"),
    "oleo": ("acido citrico", "antioxidante", "tocoferol", "tocoferois"),
    "azeite": ("acido citrico", "antioxidante", "tocoferol", "tocoferois"),
}

ALIMENTOS_BASE_GRUPO_3 = (
    "atum", "sardinha", "peixe", "milho", "ervilha", "tomate", "pepino",
    "palmito", "azeitona", "feijao", "grao de bico", "morango", "fruta",
    "abacaxi", "pessego", "goiaba", "leite", "farinha de trigo",
)
INGREDIENTES_CULINARIOS = (
    "agua", "sal", "acucar", "oleo", "oleo vegetal", "azeite", "manteiga",
    "vinagre",
)
COMPONENTES_SIMPLES_GRUPO_3 = ALIMENTOS_BASE_GRUPO_3 + INGREDIENTES_CULINARIOS + (
    "creme de leite", "fermento", "fermento biologico", "fermento lacteo",
    "coalho", "quimosina", "polpa de fruta", "suco de fruta", "suco de limao",
    "suco de tomate", "pectina", "cloreto de calcio", "culturas lacteas",
    "conservante", "benzoato de sodio", "sorbato de potassio", "emulsificante",
    "estabilizante", "espessante", "acidulante", "antioxidante", "acido citrico",
    "conservador", "nisina", "regulador de acidez", "especiaria", "especiarias",
    "tempero", "temperos", "pimenta", "alho", "louro", "aroma natural",
)

VARIANTES_OCR_GRUPO_3 = (
    "leite pasteurizado", "leite integral", "leite desnatado",
    "leite em po desnatado", "creme de leite pasteurizado",
    "fermento lacteo", "fermentos lacteos", "feijao carioca", "feijao branco",
    "oleo de soja", "oleo de girassol", "oleo de milho", "oleo de canola",
    "acidulante acido citrico", "conservador nisina", "aroma natural de endro",
)

TERMOS_RECUPERACAO_GRUPO_3 = tuple(
    sorted(
        set(COMPONENTES_SIMPLES_GRUPO_3 + VARIANTES_OCR_GRUPO_3),
        key=lambda termo: (len(termo.split()), len(termo)),
        reverse=True,
    )
)

_TERMOS_NUTRICIONAIS = (
    "informacao nutricional", "valor energetico", "porcao", "calorias",
    "carboidratos", "proteinas", "gorduras totais", "fibra alimentar", "sodio",
)


def validar_lista_ingredientes(texto: str) -> dict:
    trecho, tem_cabecalho = extrair_trecho_ingredientes(texto)
    normalizado = preprocessar(trecho)
    componentes = separar_componentes(trecho)
    if not normalizado or len(normalizado) < 3:
        return _validacao(False, trecho, componentes, "lista_ausente")

    texto_total = preprocessar(texto)
    apenas_nutricional = (
        not tem_cabecalho
        and sum(termo in texto_total for termo in _TERMOS_NUTRICIONAIS) >= 2
        and not _contem_termo_controlado(normalizado)
    )
    if apenas_nutricional:
        return _validacao(False, trecho, componentes, "somente_tabela_nutricional")

    reconhecidos = _componentes_reconhecidos(componentes)
    tem_marcador = bool(_encontrar_marcadores(normalizado))
    estrutura = tem_cabecalho or len(componentes) >= 2 or bool(re.search(r"[,;\n\r]", trecho))
    # Sem o cabeçalho, um único termo reconhecido pode ser apenas o nome na
    # frente da embalagem (por exemplo, "açúcar refinado" ou "sal"). Nessa
    # situação não há evidência suficiente de que o OCR capturou a composição.
    lista_valida = bool(reconhecidos or tem_marcador) and estrutura
    if not lista_valida:
        return _validacao(False, trecho, componentes, "texto_insuficiente")
    return _validacao(True, trecho, componentes, None)


def identificar_grupo_2(
    componentes: list[str],
    texto_completo_normalizado: str = "",
) -> dict | None:
    componentes_manteiga = ("creme de leite", "sal")
    if (
        _termo_no_texto("manteiga", texto_completo_normalizado)
        and not _termo_negado("manteiga", texto_completo_normalizado)
        and any(_corresponde_inicio(item, ("creme de leite",)) for item in componentes)
        and all(_corresponde_inicio(item, componentes_manteiga) for item in componentes)
    ):
        return _resultado_grupo(2, componentes, componentes)

    for familia, bases in FAMILIAS_GRUPO_2.items():
        bases_presentes = [item for item in componentes if item in bases]
        if not bases_presentes:
            continue
        auxiliares = AUXILIARES_GRUPO_2.get(familia, ())
        if all(item in bases or _corresponde(item, auxiliares) for item in componentes):
            return _resultado_grupo(2, componentes, bases_presentes)
    return None


def identificar_grupo_4(texto_normalizado: str) -> dict | None:
    marcadores = _encontrar_marcadores(texto_normalizado)
    if not marcadores:
        return None
    evidencias = [
        {"termo": termo, "tipo": MARCADORES_GRUPO_4[termo][0], "descricao": MARCADORES_GRUPO_4[termo][1]}
        for termo in marcadores
    ]
    return _resultado_grupo(4, marcadores, marcadores, evidencias=evidencias)


def identificar_grupo_3(
    componentes: list[str],
    texto_normalizado: str = "",
) -> dict | None:
    recuperados, nao_reconhecidos = _recuperar_componentes_controlados(
        texto_normalizado,
        TERMOS_RECUPERACAO_GRUPO_3,
    )
    if recuperados:
        if nao_reconhecidos:
            return None
        componentes = recuperados

    bases = [
        item for item in componentes
        if _corresponde_inicio(item, ALIMENTOS_BASE_GRUPO_3)
    ]
    tem_base = bool(bases)
    tem_culinario = any(
        _corresponde_inicio(item, INGREDIENTES_CULINARIOS)
        for item in componentes
    )
    conserva_acidificada = (
        any(_corresponde_inicio(item, ("tomate",)) for item in bases)
        and any(
            _corresponde_inicio(item, ("acidulante", "acido citrico"))
            for item in componentes
        )
    )
    composicao_simples = all(_corresponde(item, COMPONENTES_SIMPLES_GRUPO_3) for item in componentes)
    if tem_base and (tem_culinario or conserva_acidificada) and composicao_simples:
        return _resultado_grupo(3, componentes, componentes)
    return None


def classificar_regras(texto: str) -> dict:
    validacao = validar_lista_ingredientes(texto)
    if not validacao["valida"]:
        return {
            "score": 0, "classificacao": "pouco processado", "nova_grupo": None,
            "status_analise": "NAO_CLASSIFICADO", "motivo": validacao["motivo"],
            "ingredientes_detectados": [], "evidencias": [],
        }

    componentes = validacao["componentes"]
    texto_normalizado = preprocessar(validacao["trecho"])
    texto_completo_normalizado = preprocessar(texto)
    resultado = (
        identificar_grupo_2(componentes, texto_completo_normalizado)
        or identificar_grupo_4(texto_normalizado)
        or identificar_grupo_3(componentes, texto_normalizado)
    )
    if resultado:
        return resultado
    return {
        "score": 0, "classificacao": "pouco processado", "nova_grupo": None,
        "status_analise": "NAO_CLASSIFICADO", "motivo": "inconclusivo",
        "ingredientes_detectados": [], "evidencias": [],
    }


def _resultado_grupo(
    grupo: int,
    ingredientes: list[str],
    termos_evidencia: list[str],
    evidencias: list[dict] | None = None,
) -> dict:
    classificacao = {2: "pouco processado", 3: "processado", 4: "ultraprocessado"}[grupo]
    if evidencias is None:
        tipo = "ingrediente culinário" if grupo == 2 else "composição simples"
        descricao = (
            "Ingrediente compatível com uma família culinária processada."
            if grupo == 2 else "Componente de uma composição baseada em alimento reconhecível e ingredientes culinários."
        )
        evidencias = [{"termo": termo, "tipo": tipo, "descricao": descricao} for termo in termos_evidencia]
    return {
        "score": {2: 0, 3: 1, 4: 3}[grupo], "classificacao": classificacao,
        "nova_grupo": grupo, "status_analise": "CLASSIFICADO", "motivo": None,
        "ingredientes_detectados": list(dict.fromkeys(ingredientes)), "evidencias": evidencias,
    }


def _validacao(valida: bool, trecho: str, componentes: list[str], motivo: str | None) -> dict:
    return {"valida": valida, "trecho": trecho, "componentes": componentes, "motivo": motivo}


def _contem_termo_controlado(texto: str) -> bool:
    termos = tuple(MARCADORES_GRUPO_4) + tuple(
        termo for familia in FAMILIAS_GRUPO_2.values() for termo in familia
    ) + ALIMENTOS_BASE_GRUPO_3
    return any(_termo_no_texto(termo, texto) for termo in termos)


def _componentes_reconhecidos(componentes: list[str]) -> list[str]:
    termos = tuple(
        termo for familia in FAMILIAS_GRUPO_2.values() for termo in familia
    ) + COMPONENTES_SIMPLES_GRUPO_3
    return [item for item in componentes if _corresponde(item, termos)]


def _encontrar_marcadores(texto: str) -> list[str]:
    encontrados: list[str] = []
    # Termos longos primeiro evitam evidências redundantes como "xarope de glicose".
    for termo in sorted(MARCADORES_GRUPO_4, key=len, reverse=True):
        if (
            _termo_no_texto(termo, texto)
            and not _termo_negado(termo, texto)
            and not any(termo in existente for existente in encontrados)
        ):
            encontrados.append(termo)
    return encontrados


def _termo_no_texto(termo: str, texto: str) -> bool:
    padrao = rf"(?<![a-z0-9]){re.escape(termo)}(?:s|es)?(?![a-z0-9])"
    return re.search(padrao, texto) is not None


def _termo_negado(termo: str, texto: str) -> bool:
    padrao = rf"(?:sem|nao\s+contem)\s+(?:[a-z0-9]+\s+){{0,2}}{re.escape(termo)}(?:s|es)?"
    return re.search(padrao, texto) is not None


def _corresponde(componente: str, termos: tuple[str, ...]) -> bool:
    return any(
        componente == termo
        or componente.startswith(f"{termo} ")
        or _termo_no_texto(termo, componente)
        for termo in termos
    )


def _corresponde_inicio(componente: str, termos: tuple[str, ...]) -> bool:
    return any(
        componente == termo or componente.startswith(f"{termo} ")
        for termo in termos
    )


def _recuperar_componentes_controlados(
    texto_normalizado: str,
    termos_controlados: tuple[str, ...],
) -> tuple[list[str], list[str]]:
    """Recupera ingredientes quando o OCR remove vírgulas e quebras de linha.

    A segmentação é gulosa pelo termo controlado mais longo. Qualquer palavra
    restante invalida a recuperação, preservando o comportamento conservador.
    """
    palavras = (texto_normalizado or "").split()
    termos_tokenizados = [
        (termo, termo.split()) for termo in termos_controlados
    ]
    recuperados: list[str] = []
    nao_reconhecidos: list[str] = []
    indice = 0

    while indice < len(palavras):
        if palavras[indice] == "e":
            indice += 1
            continue

        correspondencia = None
        for termo, tokens in termos_tokenizados:
            if palavras[indice : indice + len(tokens)] == tokens:
                correspondencia = (termo, len(tokens))
                break

        if correspondencia is None:
            nao_reconhecidos.append(palavras[indice])
            indice += 1
            continue

        termo, quantidade_tokens = correspondencia
        recuperados.append(termo)
        indice += quantidade_tokens

    return list(dict.fromkeys(recuperados)), nao_reconhecidos
