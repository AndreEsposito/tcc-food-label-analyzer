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
    "BAIXO_INDICIO": 1,
}

_ROTULOS_TERMOS = {
    "glutamato monossodico": "glutamato monossódico",
    "aroma identico ao natural": "aroma idêntico ao natural",
    "acesulfame de potassio": "acesulfame de potássio",
    "benzoato de sodio": "benzoato de sódio",
    "sorbato de potassio": "sorbato de potássio",
}

_TIPOS_POR_TERMO = {
    "corante": "corante",
    "caramelo iv": "corante",
    "ins 150d": "corante",
    "aromatizante": "aromatizante",
    "aroma artificial": "aromatizante",
    "aroma identico ao natural": "aromatizante",
    "glutamato monossodico": "realçador de sabor",
    "realcador de sabor": "realçador de sabor",
    "maltodextrina": "ingrediente industrial",
    "xarope de glicose": "ingrediente industrial",
    "xarope de milho": "ingrediente industrial",
    "edulcorante": "edulcorante",
    "aspartame": "edulcorante",
    "sucralose": "edulcorante",
    "acesulfame de potassio": "edulcorante",
    "ciclamato": "edulcorante",
    "sacarina": "edulcorante",
    "gordura vegetal hidrogenada": "gordura vegetal",
    "extrato de levedura": "ingrediente industrial",
    "conservante": "conservante",
    "benzoato de sodio": "conservante",
    "sorbato de potassio": "conservante",
    "emulsificante": "emulsificante",
    "estabilizante": "estabilizante",
    "espessante": "espessante",
    "acidulante": "acidulante",
    "antiumectante": "antiumectante",
    "antioxidante": "antioxidante",
}

_DESCRICOES_POR_TIPO = {
    "aromatizante": "Pode indicar uso de substâncias para alterar ou intensificar o sabor.",
    "corante": "Pode indicar uso de substâncias para alterar a aparência do produto.",
    "conservante": "Pode indicar uso de substâncias para aumentar a durabilidade do alimento.",
    "emulsificante": "Pode indicar uso de aditivos para modificar textura e mistura dos ingredientes.",
    "edulcorante": "Pode indicar uso de substâncias para adoçar o produto sem usar açúcar comum.",
    "estabilizante": "Pode indicar uso de aditivos para manter textura, aparência ou consistência.",
    "espessante": "Pode indicar uso de aditivos para alterar a textura ou o corpo do produto.",
    "acidulante": "Pode indicar uso de aditivos para ajustar sabor ou acidez.",
    "antiumectante": "Pode indicar uso de aditivos para reduzir umidade e evitar aglomeração.",
    "antioxidante": "Pode indicar uso de aditivos para retardar alterações no alimento.",
    "realçador de sabor": "Pode indicar uso de substâncias para intensificar o sabor do produto.",
    "gordura vegetal": "Ingrediente comum em formulações industriais, especialmente quando hidrogenada.",
    "ingrediente industrial": (
        "Ingrediente frequentemente utilizado em formulações industriais para alterar "
        "textura, corpo ou composição do produto."
    ),
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
    termos_visitados = set()

    for termo in ingredientes_detectados or []:
        termo_normalizado = (termo or "").strip().lower()
        if not termo_normalizado or termo_normalizado in termos_visitados:
            continue

        termos_visitados.add(termo_normalizado)
        tipo = _TIPOS_POR_TERMO.get(termo_normalizado, "ingrediente relevante")
        evidencias.append(
            {
                "termo": _rotulo_termo(termo_normalizado),
                "tipo": tipo,
                "descricao": _DESCRICOES_POR_TIPO.get(
                    tipo,
                    "Ingrediente que pode contribuir para a avaliação do grau de processamento.",
                ),
            }
        )

    return evidencias


def gerar_explicacao_amigavel(
    classificacao: str | None = None,
    ingredientes_detectados: list[str] | None = None,
    score: int | None = None,
    status: str | None = None,
) -> dict:
    status_normalizado = _normalizar_status(status=status, classificacao=classificacao)
    evidencias = gerar_evidencias(ingredientes_detectados)
    ingredientes = [evidencia["termo"] for evidencia in evidencias]

    if status_normalizado == "ALTO_INDICIO":
        titulo = "Fortes indícios de ultraprocessamento"
        resumo = (
            "Este produto possui ingredientes e aditivos comuns em alimentos "
            "ultraprocessados."
        )
        justificativa = _justificativa_alto(ingredientes)
        orientacao = (
            "Vale consumir com atenção e comparar com produtos que tenham uma lista "
            "de ingredientes menor e com nomes mais familiares."
        )
    elif status_normalizado == "MEDIO_INDICIO":
        titulo = "Alguns indícios de processamento"
        resumo = (
            "A lista de ingredientes apresenta sinais de industrialização, mas não "
            "foram encontrados elementos suficientes para alto indício de ultraprocessamento."
        )
        justificativa = _justificativa_medio(ingredientes)
        orientacao = (
            "Observe a quantidade de ingredientes e compare com alternativas de "
            "composição mais simples."
        )
    else:
        titulo = "Poucos indícios de ultraprocessamento"
        resumo = (
            "Foram encontrados poucos ou nenhum aditivo relevante associado a produtos "
            "ultraprocessados."
        )
        justificativa = _justificativa_baixo(ingredientes)
        orientacao = (
            "Use o resultado como apoio informativo e considere que a análise depende "
            "da qualidade da imagem enviada."
        )

    return {
        "novaGrupo": _NOVA_POR_STATUS[status_normalizado],
        "titulo": titulo,
        "resumo": resumo,
        "justificativa": justificativa,
        "orientacao": orientacao,
        "evidencias": evidencias,
        "ingredientesDetectados": ingredientes,
        "aviso": AVISO_INFORMATIVO,
        "score": score,
    }


def _normalizar_status(status: str | None, classificacao: str | None) -> str:
    if status in _NOVA_POR_STATUS:
        return status

    classificacao_normalizada = (classificacao or "").strip().lower()
    return _STATUS_POR_CLASSIFICACAO.get(classificacao_normalizada, "BAIXO_INDICIO")


def _rotulo_termo(termo: str) -> str:
    return _ROTULOS_TERMOS.get(termo, termo)


def _justificativa_alto(ingredientes: list[str]) -> str:
    if not ingredientes:
        return (
            "Este produto apresenta fortes indícios de ultraprocessamento. A análise "
            "considerou sinais presentes na lista de ingredientes identificada pelo OCR."
        )

    termos = formatar_lista_termos(ingredientes)
    return (
        f"Foram identificados {termos}. Esses ingredientes costumam ser usados para "
        "modificar sabor, aparência, textura ou aumentar a durabilidade do alimento. "
        "Esses sinais indicam maior grau de formulação industrial."
    )


def _justificativa_medio(ingredientes: list[str]) -> str:
    if not ingredientes:
        return (
            "Este produto apresenta alguns sinais de processamento com base no padrão "
            "da classificação, mas não houve ingredientes críticos suficientes para "
            "alto indício."
        )

    termos = formatar_lista_termos(ingredientes)
    return (
        f"Foram identificados {termos}. Esses componentes podem estar relacionados "
        "à conservação, sabor ou textura, mas não foram suficientes para indicar "
        "alto grau de ultraprocessamento."
    )


def _justificativa_baixo(ingredientes: list[str]) -> str:
    if not ingredientes:
        return (
            "A lista de ingredientes lida pelo OCR não trouxe sinais relevantes de "
            "aditivos associados a produtos ultraprocessados."
        )

    termos = formatar_lista_termos(ingredientes)
    return (
        f"Foram identificados {termos}, mas em quantidade ou relevância insuficiente "
        "para indicar alto grau de ultraprocessamento com base nas regras atuais."
    )
