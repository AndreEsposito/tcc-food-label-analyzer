from .features import ULTRAPROCESSADOS, PROCESSADOS


def classificar_regras(features: dict) -> dict:
    score = 0
    encontrados = []

    for ingrediente, presente in features.items():
        if presente == 1:
            if ingrediente in ULTRAPROCESSADOS:
                score += 3
            elif ingrediente in PROCESSADOS:
                score += 1

            encontrados.append(ingrediente)

    tem_ultraprocessado = any(
        ingrediente in ULTRAPROCESSADOS for ingrediente in encontrados
    )

    if score >= 5:
        classificacao = "ultraprocessado"
    elif score >= 4 and tem_ultraprocessado:
        classificacao = "ultraprocessado"
    elif score >= 1:
        classificacao = "processado"
    else:
        classificacao = "pouco processado"

    return {
        "score": score,
        "classificacao": classificacao,
        "ingredientes_detectados": encontrados,
    }