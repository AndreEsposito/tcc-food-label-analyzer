import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from services.api_service import _normalizar_resposta


def test_normalizar_resposta_com_contrato_novo():
    resultado = _normalizar_resposta(
        {
            "classificacao": {
                "categoria": "ultraprocessado",
                "status": "ALTO_INDICIO",
                "novaGrupo": 4,
                "titulo": "Fortes indícios de ultraprocessamento",
                "resumo": "Resumo amigável.",
                "justificativa": "Justificativa amigável.",
                "orientacao": "Orientação educativa.",
                "evidencias": [
                    {
                        "termo": "aromatizante",
                        "tipo": "aromatizante",
                        "descricao": "Pode indicar alteração de sabor.",
                    }
                ],
                "ingredientesDetectados": ["aromatizante"],
                "aviso": "Resultado informativo.",
            }
        }
    )

    assert resultado["nova_grupo"] == 4
    assert resultado["classificacao"] == "Fortes indícios de ultraprocessamento"
    assert resultado["titulo"] == "Fortes indícios de ultraprocessamento"
    assert resultado["resumo"] == "Resumo amigável."
    assert resultado["justificativa"] == "Justificativa amigável."
    assert resultado["orientacao"] == "Orientação educativa."
    assert resultado["evidencias"][0]["termo"] == "aromatizante"
    assert resultado["ingredientes_detectados"] == ["aromatizante"]
    assert resultado["aviso"] == "Resultado informativo."


def test_normalizar_resposta_com_contrato_antigo():
    resultado = _normalizar_resposta(
        {
            "classificacao": {
                "categoria": "ultraprocessado",
                "status": "MEDIO_INDICIO",
                "justificativa": "Texto antigo.",
            }
        }
    )

    assert resultado["nova_grupo"] == 3
    assert resultado["classificacao"] == "Alimento processado"
    assert resultado["titulo"] == "Alimento processado"
    assert resultado["justificativa"] == "Texto antigo."
    assert resultado["resumo"] == ""
    assert resultado["orientacao"] == ""
    assert resultado["evidencias"] == []
    assert resultado["ingredientes_detectados"] == []
    assert resultado["aviso"] == ""
