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
    assert resultado["titulo"] == "Alimento processado"
    assert "emulsificante" in resultado["justificativa"]
    assert resultado["orientacao"]


def test_gera_explicacao_para_baixo_indicio():
    resultado = gerar_explicacao_amigavel(
        status="BAIXO_INDICIO",
        ingredientes_detectados=[],
    )

    assert resultado["novaGrupo"] == 2
    assert resultado["titulo"] == "Ingrediente culinário processado"
    assert resultado["orientacao"]


def test_gera_explicacao_para_resultado_inconclusivo():
    resultado = gerar_explicacao_amigavel(
        status="BAIXO_INDICIO",
        nova_grupo=None,
        motivo_nao_classificacao="inconclusivo",
    )
    assert resultado["novaGrupo"] is None
    assert resultado["titulo"] == "Classificação inconclusiva"
    assert resultado["evidencias"] == []


def test_gera_resultado_normal_quando_ingredientes_nao_definem_grupo():
    resultado = gerar_explicacao_amigavel(
        nova_grupo=None,
        ingredientes_detectados=["cacau", "canela"],
        motivo_nao_classificacao="grupo_indeterminado",
    )
    assert resultado["novaGrupo"] is None
    assert resultado["titulo"] == "Grupo NOVA não determinado"
    assert resultado["ingredientesDetectados"] == ["cacau", "canela"]
    assert all(item["tipo"] == "ingrediente identificado" for item in resultado["evidencias"])


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
