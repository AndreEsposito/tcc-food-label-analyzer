from .preprocess import preprocessar
from .rules import MARCADORES_GRUPO_4


AVISO_INFORMATIVO = (
    "Resultado informativo baseado na lista de ingredientes identificada pelo OCR. "
    "Esta análise não substitui a avaliação de um profissional de nutrição."
)

_STATUS_POR_CLASSIFICACAO = {
    "ultraprocessado": "ALTO_INDICIO",
    "processado": "MEDIO_INDICIO",
    "pouco processado": "BAIXO_INDICIO",
}
_NOVA_POR_STATUS = {
    "ALTO_INDICIO": 4,
    "MEDIO_INDICIO": 3,
    "BAIXO_INDICIO": 2,
}
_ROTULOS_TERMOS = {
    "glutamato monossodico": "glutamato monossódico",
    "aroma identico ao natural": "aroma idêntico ao natural",
    "acesulfame de potassio": "acesulfame de potássio",
    "acucar": "açúcar",
    "acucar refinado": "açúcar refinado",
    "acucar invertido": "açúcar invertido",
    "oleo": "óleo",
    "oleo de soja": "óleo de soja",
    "agua": "água",
    "proteina hidrolisada": "proteína hidrolisada",
    "proteina lactea": "proteína láctea",
    "solidos de xarope": "sólidos de xarope",
}
_TIPOS_POR_TERMO = {
    "corante": "corante", "caramelo iv": "corante", "ins 150d": "corante",
    "aromatizante": "aromatizante", "aroma artificial": "aromatizante",
    "aroma identico ao natural": "aromatizante",
    "glutamato monossodico": "realçador de sabor", "realcador de sabor": "realçador de sabor",
    "maltodextrina": "ingrediente industrial", "xarope de glicose": "ingrediente industrial",
    "xarope de milho": "ingrediente industrial", "edulcorante": "edulcorante",
    "aspartame": "edulcorante", "sucralose": "edulcorante",
    "acesulfame de potassio": "edulcorante", "ciclamato": "edulcorante",
    "sacarina": "edulcorante", "gordura vegetal hidrogenada": "gordura modificada",
    "extrato de levedura": "realçador de sabor",
}
_DESCRICOES_POR_TIPO = {
    "aromatizante": "Pode indicar uso de substâncias para alterar ou intensificar o sabor.",
    "corante": "Pode indicar uso de substâncias para alterar a aparência do produto.",
    "edulcorante": "Pode indicar uso de substâncias para adoçar o produto.",
    "realçador de sabor": "Pode indicar uso de substâncias para intensificar o sabor.",
    "gordura modificada": "Gordura modificada por processo industrial.",
    "ingrediente industrial": "Ingrediente frequente em formulações industriais.",
}


def formatar_lista_termos(termos: list[str]) -> str:
    termos_validos = [termo for termo in termos if termo]
    if not termos_validos:
        return ""
    if len(termos_validos) == 1:
        return termos_validos[0]
    if len(termos_validos) == 2:
        return f"{termos_validos[0]} e {termos_validos[1]}"
    return f"{', '.join(termos_validos[:-1])} e {termos_validos[-1]}"


def gerar_evidencias(ingredientes_detectados: list[str] | None) -> list[dict]:
    evidencias = []
    vistos = set()
    for termo in ingredientes_detectados or []:
        normalizado = (termo or "").strip().lower()
        if not normalizado or normalizado in vistos:
            continue
        vistos.add(normalizado)
        marcador = MARCADORES_GRUPO_4.get(preprocessar(normalizado))
        tipo = marcador[0] if marcador else _TIPOS_POR_TERMO.get(normalizado, "ingrediente relevante")
        evidencias.append({
            "termo": _rotulo_termo(normalizado),
            "tipo": tipo,
            "descricao": marcador[1] if marcador else _DESCRICOES_POR_TIPO.get(
                tipo, "Ingrediente considerado pelas regras de classificação NOVA."
            ),
        })
    return evidencias


def gerar_explicacao_amigavel(
    classificacao: str | None = None,
    ingredientes_detectados: list[str] | None = None,
    score: int | None = None,
    status: str | None = None,
    nova_grupo: int | None = None,
    motivo_nao_classificacao: str | None = None,
    evidencias: list[dict] | None = None,
) -> dict:
    if motivo_nao_classificacao == "grupo_indeterminado" and ingredientes_detectados:
        return _gerar_grupo_indeterminado(ingredientes_detectados, score)
    if motivo_nao_classificacao:
        return _gerar_nao_classificado(motivo_nao_classificacao, score)

    status_normalizado = _normalizar_status(status, classificacao)
    grupo = nova_grupo if nova_grupo in {1, 2, 3, 4} else _NOVA_POR_STATUS[status_normalizado]
    evidencias_finais = evidencias if evidencias is not None else gerar_evidencias(ingredientes_detectados)
    evidencias_finais = [
        {**item, "termo": _rotulo_termo(item.get("termo", ""))}
        for item in evidencias_finais
    ]
    ingredientes = list(dict.fromkeys(_rotulo_termo(item) for item in (ingredientes_detectados or [])))

    por_denominacao = any(item.get("tipo") == "denominação do produto" for item in evidencias_finais)
    if grupo == 1:
        titulo = "Alimento in natura ou minimamente processado"
        resumo = "A composição identificada é compatível com um alimento in natura ou minimamente processado."
        orientacao = "Confira se a lista foi lida por completo e compare com outros produtos de composição simples."
    elif grupo == 4:
        titulo = "Fortes indícios de ultraprocessamento"
        resumo = "Este produto possui marcadores fortes comuns em formulações ultraprocessadas."
        orientacao = "Compare a composição com a de produtos semelhantes e prefira opções à base de alimentos e ingredientes culinários."
    elif grupo == 3:
        titulo = "Alimento processado"
        resumo = "A composição combina um alimento reconhecível com ingredientes culinários."
        orientacao = "Observe a quantidade de sal ou açúcar e compare com alternativas de composição simples."
    else:
        titulo = "Ingrediente culinário processado"
        resumo = "A composição é compatível com um ingrediente culinário processado do grupo 2 da NOVA."
        orientacao = "Use com moderação como parte do preparo de alimentos e refeições."
        if por_denominacao:
            resumo = "O produto foi identificado como açúcar refinado pela denominação na embalagem."

    justificativa = _justificar_grupo(grupo, ingredientes, evidencias_finais)

    return {
        "novaGrupo": grupo, "titulo": titulo, "resumo": resumo,
        "justificativa": justificativa, "orientacao": orientacao,
        "evidencias": evidencias_finais, "ingredientesDetectados": ingredientes,
        "aviso": (
            "Resultado informativo baseado na denominação do produto. Confirme a composição no rótulo."
            if por_denominacao else AVISO_INFORMATIVO
        ), "score": score,
    }


def _justificar_grupo(grupo: int, ingredientes: list[str], evidencias: list[dict]) -> str:
    # A justificativa cita exemplos; as listas completas continuam nos campos próprios.
    termos = formatar_lista_termos(ingredientes[:4])
    leitura = f"Na lista lida, foram identificados {termos}. " if termos else ""
    normalizados = [preprocessar(item) for item in ingredientes]

    if grupo == 1:
        if any(item.startswith(("aveia", "flocos de aveia")) for item in normalizados):
            motivo = "A composição preserva a aveia como alimento-base, sem adição identificada de sal, açúcar ou marcadores de ultraprocessamento."
        elif any(item in {"fermento lacteo", "culturas lacteas"} for item in normalizados):
            motivo = "O leite e as culturas de fermentação formam uma composição compatível com iogurte natural sem açúcar adicionado. A fermentação, por si só, não caracteriza ultraprocessamento."
        elif any(item.startswith("leite") for item in normalizados):
            motivo = "A composição mantém o leite como alimento-base."
            if any("lactase" in item for item in normalizados):
                motivo += " A lactase é uma enzima usada para quebrar a lactose e, neste contexto, não define ultraprocessamento."
            if any("estabilizant" in item or "fosfato" in item or item == "citrato de sodio" for item in normalizados):
                motivo += " Os estabilizantes reconhecidos nesta composição do leite não bastam para enquadrá-lo como ultraprocessado."
        else:
            motivo = "A composição identificada é compatível com um alimento que preserva suas características básicas, sem ingredientes que sustentem um grupo de maior processamento."
        return leitura + motivo + " Por isso, o resultado é compatível com NOVA 1."

    if grupo == 2:
        if any(item.get("tipo") == "denominação do produto" for item in evidencias):
            return (
                "A embalagem foi reconhecida pela denominação açúcar refinado e pelo peso líquido; a lista de ingredientes não foi lida. "
                "O açúcar é um ingrediente culinário obtido de alimentos e usado para adoçar preparações, o que sustenta NOVA 2. "
                "Confirme a composição no rótulo."
            )
        if any(item.startswith("acucar") for item in normalizados):
            uso = "adoçar preparações"
        elif any(item.startswith(("sal", "cloreto de sodio")) for item in normalizados) and not any(
            item.startswith(("creme de leite", "manteiga")) for item in normalizados
        ):
            uso = "temperar e conservar alimentos"
        else:
            uso = "cozinhar, temperar ou compor preparações"
        return (
            leitura + f"A composição é compatível com um ingrediente culinário usado para {uso}. "
            "Esse tipo de produto é obtido por extração ou transformação de alimentos ou de fontes naturais e pertence ao NOVA 2. "
            "Seu uso culinário o diferencia de um alimento pronto para consumo."
        )

    if grupo == 3:
        return (
            leitura + "A composição combina um alimento-base com sal, açúcar ou outros ingredientes culinários, "
            "usados no preparo ou na conservação, mantendo o alimento reconhecível. "
            "Essa combinação sustenta NOVA 3; na lista analisada, não foram identificados marcadores fortes de ultraprocessamento."
        )

    funcoes = {
        "aromatizante": "modificar aroma e sabor",
        "corante": "alterar ou reforçar a cor",
        "edulcorante": "adoçar com edulcorantes",
        "realçador de sabor": "intensificar o sabor",
        "emulsificante": "ajustar a textura e estabilizar misturas",
        "espessante": "modificar a textura e a consistência",
        "gordura modificada": "incorporar gorduras modificadas industrialmente",
        "ingrediente industrial": "incorporar frações ou substâncias de uso industrial",
        "açúcar industrial": "incorporar açúcares transformados para uso industrial",
    }
    usos = list(dict.fromkeys(
        funcoes[item["tipo"]] for item in evidencias if item.get("tipo") in funcoes
    ))
    papel = (
        f"Esses marcadores são usados para {formatar_lista_termos(usos[:3])}. "
        if usos else "Esses ingredientes são marcadores de formulação industrial reconhecidos pelas regras. "
    )
    return (
        leitura + papel + "Sua presença sustenta NOVA 4, por indicar uma formulação que vai além "
        "da combinação de alimentos com ingredientes culinários. A classificação considera o tipo dos ingredientes, não apenas a quantidade de itens na lista."
    )


def _gerar_nao_classificado(motivo: str, score: int | None) -> dict:
    if motivo == "inconclusivo":
        titulo = "Classificação inconclusiva"
        resumo = "A lista de ingredientes foi identificada, mas não apresentou informações suficientes para determinar com segurança o grupo NOVA."
        justificativa = "A composição não correspondeu de forma segura às regras controladas dos grupos 1, 2, 3 ou 4."
        orientacao = "Confira se toda a lista de ingredientes está visível e tente novamente com uma imagem mais nítida."
        aviso = AVISO_INFORMATIVO
    else:
        titulo = "Não foi possível classificar o produto"
        resumo = "A imagem não apresentou informações suficientes para identificar os ingredientes."
        justificativa = "Não foi possível identificar uma lista de ingredientes legível na imagem enviada."
        orientacao = "Envie uma nova foto enquadrando apenas a lista de ingredientes, com boa iluminação e nitidez."
        aviso = "O resultado depende da qualidade e da legibilidade da imagem enviada."
    return {
        "novaGrupo": None, "titulo": titulo, "resumo": resumo,
        "justificativa": justificativa, "orientacao": orientacao,
        "evidencias": [], "ingredientesDetectados": [], "aviso": aviso,
        "score": score,
    }


def _gerar_grupo_indeterminado(
    ingredientes_detectados: list[str],
    score: int | None,
) -> dict:
    ingredientes = list(dict.fromkeys(
        _rotulo_termo(item) for item in ingredientes_detectados if item
    ))
    termos = formatar_lista_termos(ingredientes)
    evidencias = [
        {
            "termo": ingrediente,
            "tipo": "ingrediente identificado",
            "descricao": (
                "Identificado na lista, mas sem evidência suficiente para definir "
                "com segurança o grupo NOVA."
            ),
        }
        for ingrediente in ingredientes
    ]
    return {
        "novaGrupo": None,
        "titulo": "Grupo NOVA não determinado",
        "resumo": (
            "Os ingredientes foram identificados, mas as regras não permitem "
            "determinar o grupo NOVA com segurança."
        ),
        "justificativa": (
            f"Foram identificados {termos}, porém não há evidência suficiente "
            "para atribuir os grupos NOVA 1, 2, 3 ou 4."
        ),
        "orientacao": (
            "Considere a lista apresentada como apoio informativo e compare o "
            "produto com alternativas de composição mais simples."
        ),
        "evidencias": evidencias,
        "ingredientesDetectados": ingredientes,
        "aviso": AVISO_INFORMATIVO,
        "score": score,
    }


def _normalizar_status(status: str | None, classificacao: str | None) -> str:
    if status in _NOVA_POR_STATUS:
        return status
    return _STATUS_POR_CLASSIFICACAO.get((classificacao or "").strip().lower(), "BAIXO_INDICIO")


def _rotulo_termo(termo: str) -> str:
    return _ROTULOS_TERMOS.get(termo, termo)
