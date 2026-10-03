import pytest

import packages.classification_core.ml as ml_module
from packages.classification_core.pipeline import classificar


@pytest.mark.parametrize("texto", [
    "", "   ... ---   ",
    "INFORMAÇÃO NUTRICIONAL\nPorção 30 g\nValor energético 120 kcal\nCarboidratos 20 g\nSódio 30 mg",
    "Ingredientes: informação nutricional, porção 30 g, valor energético 120 kcal.",
    "Marca Boa Vida. O melhor sabor para sua família.",
])
def test_texto_sem_lista_suficiente_nao_e_classificado(texto):
    resultado = classificar(texto)
    assert resultado["status_analise"] == "NAO_CLASSIFICADO"
    assert resultado["nova_grupo"] is None
    assert resultado["explicacao_amigavel"]["evidencias"] == []


@pytest.mark.parametrize("texto", [
    "Ingredientes: AÇÚCAR REFINADO.", "Ingredientes: açúcar cristal",
    "Ingredientes: Azeite de Oliva Extravirgem",
    "INGREDIENTES:\nSAL MARINHO; iodato de potássio; antiumectante dióxido de silício.",
    "Ingredientes: óleo de soja, antioxidante ácido cítrico.",
])
def test_identifica_grupo_2_com_variacoes_de_ocr(texto):
    resultado = classificar(texto)
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] == 2
    assert resultado["classificacao_final"] == "pouco processado"


@pytest.mark.parametrize("texto", [
    "Ingredientes: Sacarose de cana-de-açúcar.",
    "Azeite de oliva refinado e azeite de oliva virgem.",
    "MANTEIGA EXTRA SEM SAL\nINGREDIENTES: creme de leite pasteurizado.",
    "Manteiga extra com sal. Ingredientes: creme de leite pasteurizado e sal.",
])
def test_identifica_variantes_de_grupo_2_presentes_no_dataset(texto):
    resultado = classificar(texto)
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] == 2


def test_creme_de_leite_sem_contexto_de_manteiga_permanece_inconclusivo():
    resultado = classificar("Ingredientes: creme de leite pasteurizado e sal.")
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] is None
    assert resultado["ingredientes_detectados"] == ["creme de leite pasteurizado", "sal"]


def test_manteiga_negada_no_rotulo_nao_ativa_regra_contextual():
    resultado = classificar(
        "Creme culinário não contém manteiga. Ingredientes: creme de leite pasteurizado e sal."
    )
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] is None


def test_composicao_com_acucar_e_aromatizante_nao_vira_grupo_2():
    assert classificar("Ingredientes: açúcar, cacau, maltodextrina e aromatizante.")["nova_grupo"] == 4


def test_frase_unica_com_componentes_extras_nao_vira_grupo_2():
    assert classificar("Ingredientes: açúcar cacau aromatizante.")["nova_grupo"] == 4


@pytest.mark.parametrize("texto", [
    "atum, água e sal", "INGREDIENTES:\nMILHO; ÁGUA; SAL.", "morango e açúcar",
    "fruta, água e açúcar", "leite, sal, fermento e coalho",
    "pepino, água, vinagre e sal", "farinha de trigo, água, sal e fermento biológico",
    "tomate, sal e açúcar",
    "tomate, água, sal e conservante",
])
def test_identifica_grupo_3_com_alimento_base_e_ingredientes_culinarios(texto):
    resultado = classificar(texto)
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] == 3
    assert resultado["classificacao_final"] == "processado"


@pytest.mark.parametrize("texto", [
    "Leite pasteurizado, sal e quimosina.",
    "Leite pasteurizado, creme de leite, sal, quimosina, regulador de acidez e conservador nisina.",
    "Morango, açúcar, pectina e suco de limão.",
    "Goiaba, açúcar, suco de limão e pectina.",
    "Tomate, suco de tomate e acidulante ácido cítrico.",
    "Pepino, vinagre, água, açúcar, sal e especiarias.",
    "Sardinha, óleo, pimenta, água e sal.",
    "Água, feijão carioca, óleo de girassol, sal, alho e louro.",
])
def test_identifica_composicoes_de_grupo_3_presentes_no_dataset(texto):
    assert classificar(texto)["nova_grupo"] == 3


@pytest.mark.parametrize("texto", [
    "atum agua e sal",
    "atum agua oleo vegetal e sal",
    "leite pasteurizado sal e quimosina",
    "leite pasteurizado creme de leite sal quimosina regulador de acidez e conservador nisina",
    "morango acucar pectina e suco de limao",
    "goiaba acucar suco de limao e pectina",
    "pessego agua e acucar",
    "tomate suco de tomate e acidulante acido citrico",
    "tomate acucar e sal",
    "pepino vinagre agua acucar sal e especiarias",
    "sardinha oleo pimenta agua e sal",
    "agua feijao carioca oleo de girassol sal alho e louro",
    "feijao branco agua e sal",
])
def test_recupera_grupo_3_quando_ocr_remove_pontuacao(texto):
    resultado = classificar(texto)
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] == 3


def test_recuperacao_sem_pontuacao_rejeita_palavra_nao_controlada():
    resultado = classificar("atum ingrediente desconhecido agua e sal")
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] is None
    assert resultado["ingredientes_detectados"]


@pytest.mark.parametrize("texto", [
    "Leite integral e fermento lácteo.",
    "Leite integral, leite em pó desnatado e fermento lácteo.",
    "Leite desnatado, creme de leite e fermentos lácteos.",
])
def test_iogurte_natural_simples_nao_e_promovido_ao_grupo_3(texto):
    resultado = classificar(texto)
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] == 1
    assert resultado["ingredientes_detectados"]


@pytest.mark.parametrize("texto, marcador", [
    ("água, açúcar, corantes e AROMATIZANTES", "aromatizante"),
    ("farinha, açúcar, maltodextrina", "maltodextrina"),
    ("milho, água, sal, amido modificado", "amido modificado"),
    ("água, suco, edulcorante sucralose", "edulcorante"),
    ("atum, água, sal e aroma idêntico ao natural", "aroma identico ao natural"),
    ("água, açúcar, INS 150D", "ins 150d"),
    ("proteína hidrolisada; óleo; sal", "proteina hidrolisada"),
    ("proteínas hidrolisadas; óleos vegetais; sal", "proteina hidrolisada"),
    ("leite integral, leite em pó desnatado, proteínas lácteas e fermento lácteo", "proteina lactea"),
    ("água, açúcar e aroma artificial", "aroma artificial"),
    ("água, açúcar e aromas artificiais", "aroma artificial"),
    ("pepino, vinagre, água, açúcar, sal, especiarias e aroma natural de endro", "aroma natural"),
    ("pepino vinagre agua acucar sal especiarias e aroma natural de endro", "aroma natural"),
    ("água, acessulfame-K", "acesulfame de potassio"),
    ("mono e diglicerídeos de ácidos graxos, farinha e água", "mono e diglicerideos de acidos graxos"),
    ("farinha, gordura vegetal interesterificada e aromatizante", "gordura interesterificada"),
    ("milho, realçadores de sabor e corantes", "realcador de sabor"),
])
def test_marcador_forte_prevalece_e_identifica_grupo_4(texto, marcador):
    resultado = classificar(texto)
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] == 4
    assert marcador in resultado["ingredientes_detectados"]
    assert all(item["tipo"] and item["descricao"] for item in resultado["evidencias"])


def test_lista_valida_mas_ambigua_fica_inconclusiva():
    resultado = classificar("Ingredientes: farinha de trigo, cacau.")
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] is None
    assert resultado["ingredientes_detectados"] == ["farinha de trigo", "cacau"]
    assert resultado["explicacao_amigavel"]["titulo"] == "Grupo NOVA não determinado"


def test_lista_com_ingredientes_desconhecidos_retorna_resultado_sem_grupo():
    resultado = classificar("Ingredientes: cacau, canela.")
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] is None
    assert resultado["ingredientes_detectados"] == ["cacau", "canela"]
    assert resultado["explicacao_amigavel"]["evidencias"]


def test_auxiliar_moderado_isolado_nao_define_grupo_3():
    resultado = classificar("Ingredientes: conservante, estabilizante.")
    assert resultado["status_analise"] == "CLASSIFICADO"
    assert resultado["nova_grupo"] is None


def test_duplicacao_pontuacao_e_caixa_nao_duplicam_evidencias():
    resultado = classificar("INGREDIENTES: CORANTE, corante; Aromatizante!\nAROMATIZANTE.")
    assert resultado["nova_grupo"] == 4
    assert sorted(resultado["ingredientes_detectados"]) == ["aromatizante", "corante"]


def test_termo_negado_fora_de_uma_lista_nao_sustenta_classificacao():
    assert classificar("Produto sem corantes artificiais. Marca Sabor Natural.")["status_analise"] == "NAO_CLASSIFICADO"


@pytest.mark.parametrize("texto", [
    "açúcar refinado",
    "sal refinado",
    "azeite de oliva extravirgem",
    "aromatizante",
])
def test_termo_isolado_sem_evidencia_de_lista_fica_inconclusivo(texto):
    resultado = classificar(texto)

    assert resultado["status_analise"] == "NAO_CLASSIFICADO"
    assert resultado["nova_grupo"] is None
    assert resultado["ingredientes_detectados"] == []


def test_falha_do_random_forest_nao_impede_resultado_heuristico(monkeypatch):
    monkeypatch.setattr(ml_module, "carregar_modelo", lambda: (_ for _ in ()).throw(OSError("pickle inválido")))
    resultado = classificar("Ingredientes: atum, água e sal.")
    assert resultado["nova_grupo"] == 3
    assert resultado["ia"]["disponivel"] is False
