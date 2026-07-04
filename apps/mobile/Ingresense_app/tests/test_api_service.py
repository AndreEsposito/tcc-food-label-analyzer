import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from requests import Response

from services.api_service import (
    _erro_por_codigo,
    _extrair_detalhe_servidor,
    _normalizar_resposta,
)


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


def test_erro_por_codigo_preserva_codigo_http_real():
    resultado = _erro_por_codigo(502, "Falha ao processar OCR.")

    assert resultado["codigo"] == 502
    assert "0" not in resultado["erro"]
    assert resultado["detalhe_tecnico"] == "Falha ao processar OCR."


def test_extrair_detalhe_servidor_lendo_detail_json():
    response = Response()
    response.status_code = 422
    response._content = b'{"detail":"Nao foi possivel extrair texto da imagem."}'
    response.headers["Content-Type"] = "application/json"

    assert _extrair_detalhe_servidor(response) == "Nao foi possivel extrair texto da imagem."
