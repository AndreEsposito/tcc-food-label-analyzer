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
        tipo = _TIPOS_POR_TERMO.get(normalizado, "ingrediente relevante")
        evidencias.append({
            "termo": _rotulo_termo(normalizado),
            "tipo": tipo,
            "descricao": _DESCRICOES_POR_TIPO.get(
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
    if motivo_nao_classificacao:
        return _gerar_nao_classificado(motivo_nao_classificacao, score)

    status_normalizado = _normalizar_status(status, classificacao)
    grupo = nova_grupo if nova_grupo in {2, 3, 4} else _NOVA_POR_STATUS[status_normalizado]
    evidencias_finais = evidencias if evidencias is not None else gerar_evidencias(ingredientes_detectados)
    evidencias_finais = [
        {**item, "termo": _rotulo_termo(item.get("termo", ""))}
        for item in evidencias_finais
    ]
    ingredientes = list(dict.fromkeys(_rotulo_termo(item) for item in (ingredientes_detectados or [])))
    termos = formatar_lista_termos(ingredientes)

    if grupo == 4:
        titulo = "Fortes indícios de ultraprocessamento"
        resumo = "Este produto possui marcadores fortes comuns em formulações ultraprocessadas."
        justificativa = (
            f"Foram identificados {termos}. Esses marcadores indicam maior grau de formulação industrial."
            if termos else "A composição apresenta marcadores fortes de formulação industrial."
        )
        orientacao = "Compare com produtos que tenham uma lista de ingredientes menor e com nomes mais familiares."
    elif grupo == 3:
        titulo = "Alimento processado"
        resumo = "A composição combina um alimento reconhecível com ingredientes culinários."
        justificativa = (
            f"Foram identificados {termos}, sem marcadores fortes de formulação ultraprocessada."
            if termos else "A composição é compatível com um alimento processado simples."
        )
        orientacao = "Observe a quantidade de sal ou açúcar e compare com alternativas de composição simples."
    else:
        titulo = "Ingrediente culinário processado"
        resumo = "A composição é compatível com um ingrediente culinário processado do grupo 2 da NOVA."
        justificativa = (
            f"A lista contém {termos}, em uma composição simples e compatível com uso culinário."
            if termos else "A composição identificada é simples e compatível com uso culinário."
        )
        orientacao = "Use com moderação como parte do preparo de alimentos e refeições."

    return {
        "novaGrupo": grupo, "titulo": titulo, "resumo": resumo,
        "justificativa": justificativa, "orientacao": orientacao,
        "evidencias": evidencias_finais, "ingredientesDetectados": ingredientes,
        "aviso": AVISO_INFORMATIVO, "score": score,
    }


def _gerar_nao_classificado(motivo: str, score: int | None) -> dict:
    if motivo == "inconclusivo":
        titulo = "Classificação inconclusiva"
        resumo = "A lista de ingredientes foi identificada, mas não apresentou informações suficientes para determinar com segurança o grupo NOVA."
        justificativa = "A composição não correspondeu de forma segura às regras controladas dos grupos 2, 3 ou 4."
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


def _normalizar_status(status: str | None, classificacao: str | None) -> str:
    if status in _NOVA_POR_STATUS:
        return status
    return _STATUS_POR_CLASSIFICACAO.get((classificacao or "").strip().lower(), "BAIXO_INDICIO")


def _rotulo_termo(termo: str) -> str:
    return _ROTULOS_TERMOS.get(termo, termo)
