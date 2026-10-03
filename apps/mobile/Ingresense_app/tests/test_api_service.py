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


def test_contrato_antigo_sem_grupo_explicito_fica_inconclusivo():
    resultado = _normalizar_resposta(
        {
            "classificacao": {
                "categoria": "ultraprocessado",
                "status": "MEDIO_INDICIO",
                "justificativa": "Texto antigo.",
            }
        }
    )

    assert resultado["nova_grupo"] is None
    assert resultado["nao_classificado"] is True
    assert resultado["classificacao"] == "Classificação inconclusiva"
    assert resultado["titulo"] == "Classificação inconclusiva"
    assert resultado["justificativa"] == "Texto antigo."
    assert resultado["resumo"] == ""
    assert resultado["orientacao"] == ""
    assert resultado["evidencias"] == []
    assert resultado["ingredientes_detectados"] == []
    assert resultado["aviso"] == ""


def test_contrato_com_nova_1_explicito_e_aceito():
    resultado = _normalizar_resposta(
        {
            "status": "CLASSIFICADO",
            "classificacao": {
                "categoria": "ultraprocessado",
                "status": "BAIXO_INDICIO",
                "novaGrupo": 1,
                "titulo": "Alimento in natura ou minimamente processado",
                "justificativa": "Ingredientes compatíveis com NOVA 1.",
            },
        }
    )
    assert resultado["nova_grupo"] == 1
    assert "nao_classificado" not in resultado


def test_contrato_antigo_sem_nova_grupo_fica_inconclusivo():
    resultado = _normalizar_resposta(
        {
            "status": "CLASSIFICADO",
            "classificacao": {
                "categoria": "ultraprocessado",
                "status": "BAIXO_INDICIO",
            },
        }
    )
    assert resultado["nova_grupo"] is None
    assert resultado["nao_classificado"] is True


def test_status_desconhecido_nao_e_convertido_em_grupo_1_ou_4():
    resultado = _normalizar_resposta(
        {
            "status": "CLASSIFICADO",
            "classificacao": {
                "categoria": "ultraprocessado",
                "status": "DESCONHECIDO",
                "novaGrupo": 1,
            },
        }
    )
    assert resultado["nova_grupo"] is None
    assert resultado["nao_classificado"] is True


def test_resposta_antiga_com_lista_identificada_vira_nova_indeterminada():
    resultado = _normalizar_resposta(
        {
            "status": "NAO_CLASSIFICADO",
            "classificacao": {
                "categoria": "ultraprocessado",
                "status": "BAIXO_INDICIO",
                "novaGrupo": None,
                "titulo": "Classificação inconclusiva",
                "resumo": "A lista de ingredientes foi identificada, mas não apresentou informações suficientes para determinar o grupo NOVA.",
                "orientacao": "Fotografe novamente.",
                "evidencias": [],
                "ingredientesDetectados": [],
            },
        }
    )
    assert resultado["nova_grupo"] is None
    assert resultado["grupo_indeterminado"] is True
    assert "nao_classificado" not in resultado
    assert resultado["titulo"] == "Grupo NOVA não determinado"


def test_resposta_sem_ingredientes_continua_nao_classificada():
    resultado = _normalizar_resposta(
        {
            "status": "NAO_CLASSIFICADO",
            "classificacao": {
                "categoria": "ultraprocessado",
                "status": "BAIXO_INDICIO",
                "novaGrupo": None,
                "titulo": "Não foi possível classificar o produto",
                "resumo": "A imagem não apresentou ingredientes identificáveis.",
                "ingredientesDetectados": [],
            },
        }
    )
    assert resultado["nova_grupo"] is None
    assert resultado["nao_classificado"] is True
    assert "grupo_indeterminado" not in resultado


def test_normalizar_resultado_com_ingredientes_e_grupo_nulo_sem_erro():
    resultado = _normalizar_resposta(
        {
            "status": "CLASSIFICADO",
            "classificacao": {
                "categoria": "ultraprocessado",
                "status": "BAIXO_INDICIO",
                "novaGrupo": None,
                "titulo": "Grupo NOVA não determinado",
                "resumo": "Ingredientes identificados sem grupo seguro.",
                "justificativa": "Foram identificados cacau e canela.",
                "orientacao": "Compare produtos semelhantes.",
                "evidencias": [
                    {
                        "termo": "cacau",
                        "tipo": "ingrediente identificado",
                        "descricao": "Sem evidência suficiente para definir o grupo.",
                    }
                ],
                "ingredientesDetectados": ["cacau", "canela"],
            },
        }
    )
    assert resultado["nova_grupo"] is None
    assert resultado["grupo_indeterminado"] is True
    assert "nao_classificado" not in resultado
    assert resultado["titulo"] == "Grupo NOVA não determinado"


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
