import pytest

from packages.classification_core.explanation_generator import (
    formatar_lista_termos,
    gerar_explicacao_amigavel,
)
from packages.classification_core.pipeline import classificar


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
        ingredientes_detectados=["tomate", "sal"],
    )

    assert resultado["novaGrupo"] == 3
    assert resultado["titulo"] == "Alimento processado"
    assert "tomate e sal" in resultado["justificativa"]
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


@pytest.mark.parametrize("texto, grupo, explicacao, ausente", [
    ("Ingredientes: aveia em flocos.", 1, "preserva a aveia", "iogurte"),
    ("Ingredientes: leite integral e fermento lácteo.", 1, "A fermentação, por si só", "lactase"),
    ("Ingredientes: leite UHT integral.", 1, "mantém o leite", "estabilizantes"),
    ("Ingredientes: leite semidesnatado, enzima lactase, citrato de sódio.", 1,
     "A lactase é uma enzima", "iogurte"),
    ("Ingredientes: açúcar refinado.", 2, "adoçar preparações", "temperar e conservar"),
    ("Ingredientes: sal e iodato de potássio.", 2, "temperar e conservar", "adoçar"),
    ("Ingredientes: azeite de oliva.", 2, "cozinhar, temperar", "adoçar"),
    ("Ingredientes: tomate, açúcar e sal.", 3, "mantendo o alimento reconhecível", "modificar aroma"),
    ("Ingredientes: açúcar e aromatizante.", 4, "modificar aroma e sabor", "reforçar a cor"),
    ("Ingredientes: açúcar e corante.", 4, "alterar ou reforçar a cor", "modificar aroma"),
    ("Ingredientes: açúcar e lecitina.", 4, "ajustar a textura", "reforçar a cor"),
    ("Ingredientes: açúcar e maltodextrina.", 4, "frações ou substâncias de uso industrial", "reforçar a cor"),
])
def test_justificativa_acompanha_grupo_e_composicao(texto, grupo, explicacao, ausente):
    resultado = classificar(texto)
    justificativa = resultado["explicacao_amigavel"]["justificativa"]
    assert resultado["nova_grupo"] == grupo
    assert f"NOVA {grupo}" in justificativa
    assert explicacao in justificativa
    assert ausente not in justificativa


def test_denominacao_nao_inventa_lista_de_ingredientes():
    resultado = classificar("Açúcar refinado\nPeso líquido 1 kg")["explicacao_amigavel"]
    assert resultado["novaGrupo"] == 2
    assert "a lista de ingredientes não foi lida" in resultado["justificativa"]
    assert "Na lista lida" not in resultado["justificativa"]
    assert resultado["ingredientesDetectados"] == []


def test_justificativa_limita_exemplos_sem_perder_ingredientes_ou_evidencias():
    termos = ["aromatizante", "corante", "lecitina", "maltodextrina", "sucralose"]
    resultado = gerar_explicacao_amigavel(nova_grupo=4, ingredientes_detectados=termos)
    assert "maltodextrina" in resultado["justificativa"]
    assert "sucralose" not in resultado["justificativa"]
    assert resultado["ingredientesDetectados"] == termos
    assert len(resultado["evidencias"]) == len(termos)


@pytest.mark.parametrize("grupo", [1, 2, 3, 4])
def test_justificativa_sem_ingredientes_nao_inventa_termos(grupo):
    resultado = gerar_explicacao_amigavel(nova_grupo=grupo)
    assert f"NOVA {grupo}" in resultado["justificativa"]
    assert "identificados ." not in resultado["justificativa"]
    assert "Na lista lida" not in resultado["justificativa"]
