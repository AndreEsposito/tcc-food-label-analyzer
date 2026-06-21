from .preprocess import preprocessar
from .features import extrair_features
from .rules import classificar_regras
from .explain import gerar_explicacao
from .explanation_generator import gerar_explicacao_amigavel
from .ml import classificar_ml


def classificar(texto: str) -> dict:
    texto_processado = preprocessar(texto)
    features = extrair_features(texto_processado)

    resultado_regras = classificar_regras(features)
    resultado_ia = classificar_ml(features)

    explicacao = gerar_explicacao(
        resultado_regras["classificacao"],
        resultado_regras["ingredientes_detectados"]
    )
    explicacao_amigavel = gerar_explicacao_amigavel(
        classificacao=resultado_regras["classificacao"],
        ingredientes_detectados=resultado_regras["ingredientes_detectados"],
        score=resultado_regras["score"],
    )

    return {
        "texto_original": texto,
        "texto_processado": texto_processado,
        "features": features,
        "regras": resultado_regras,
        "ia": resultado_ia,
        "classificacao_final": resultado_regras["classificacao"],
        "explicacao": explicacao,
        "explicacao_amigavel": explicacao_amigavel,
        "evidencias": explicacao_amigavel["evidencias"],
        "ingredientes_detectados": resultado_regras["ingredientes_detectados"],
    }
