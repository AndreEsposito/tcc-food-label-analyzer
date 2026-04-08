from .preprocess import preprocessar
from .features import extrair_features
from .rules import classificar_regras
from .explain import gerar_explicacao


def classificar(texto: str) -> dict:
    texto_processado = preprocessar(texto)
    features = extrair_features(texto_processado)
    resultado = classificar_regras(features)

    explicacao = gerar_explicacao(
        resultado["classificacao"],
        resultado["ingredientes_detectados"]
    )

    return {
        "texto_original": texto,
        "texto_processado": texto_processado,
        "features": features,
        **resultado,
        "explicacao": explicacao,
    }