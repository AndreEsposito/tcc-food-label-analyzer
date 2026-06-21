from packages.classification_core.explanation_generator import (
    formatar_lista_termos,
    gerar_explicacao_amigavel,
)


def test_gera_explicacao_para_alto_indicio():
    resultado = gerar_explicacao_amigavel(
        status="ALTO_INDICIO",
        ingredientes_detectados=["aromatizante", "corante", "conservante"],
    )

    assert resultado["novaGrupo"] == 4
    assert resultado["titulo"] == "Fortes indícios de ultraprocessamento"
    assert resultado["resumo"]
    assert "aromatizante, corante e conservante" in resultado["justificativa"]
    assert resultado["orientacao"]
    assert resultado["evidencias"][0]["tipo"] == "aromatizante"


def test_gera_explicacao_para_medio_indicio():
    resultado = gerar_explicacao_amigavel(
        status="MEDIO_INDICIO",
        ingredientes_detectados=["emulsificante"],
    )

    assert resultado["novaGrupo"] == 3
    assert resultado["titulo"] == "Alguns indícios de processamento"
    assert "emulsificante" in resultado["justificativa"]
    assert resultado["orientacao"]


def test_gera_explicacao_para_baixo_indicio():
    resultado = gerar_explicacao_amigavel(
        status="BAIXO_INDICIO",
        ingredientes_detectados=[],
    )

    assert resultado["novaGrupo"] == 1
    assert resultado["titulo"] == "Poucos indícios de ultraprocessamento"
    assert "OCR" in resultado["justificativa"]
    assert resultado["orientacao"]


def test_gera_explicacao_com_lista_vazia_de_evidencias():
    resultado = gerar_explicacao_amigavel(
        classificacao="ultraprocessado",
        ingredientes_detectados=[],
    )

    assert resultado["evidencias"] == []
    assert resultado["ingredientesDetectados"] == []
    assert resultado["justificativa"]


def test_formata_lista_de_termos_em_portugues():
    assert formatar_lista_termos(["aromatizante"]) == "aromatizante"
    assert (
        formatar_lista_termos(["aromatizante", "corante"])
        == "aromatizante e corante"
    )
    assert (
        formatar_lista_termos(["aromatizante", "corante", "conservante"])
        == "aromatizante, corante e conservante"
    )
