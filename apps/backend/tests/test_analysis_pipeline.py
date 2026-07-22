import pytest

import app.services.analysis_pipeline as analysis_pipeline_module
from app.services.analysis_pipeline import AnalysisPipeline
from app.services.exceptions import OCRNoTextError


class StubOCR:
    def __init__(self, response_text: str | None):
        self.response_text = response_text

    def extract_text(self, image_bytes: bytes) -> str:
        if self.response_text is None:
            raise OCRNoTextError("sem texto")
        return self.response_text


@pytest.mark.parametrize(
    ("classificacao_final", "expected_status"),
    [
        ("ultraprocessado", "ALTO_INDICIO"),
        ("processado", "MEDIO_INDICIO"),
        ("pouco processado", "BAIXO_INDICIO"),
    ],
)
def test_analysis_pipeline_keeps_category_fixed_for_all_statuses(
    monkeypatch,
    classificacao_final,
    expected_status,
):
    ocr = StubOCR(
        "INGREDIENTES: acucar, farinha de trigo, aromatizante, corante. ALERGICOS: contem gluten."
    )
    monkeypatch.setattr(
        analysis_pipeline_module,
        "classificar",
        lambda texto: {
            "classificacao_final": classificacao_final,
            "explicacao": "Classificacao gerada a partir dos ingredientes detectados.",
        },
    )
    pipeline = AnalysisPipeline(ocr_service=ocr)

    result = pipeline.run(image_bytes=b"img")

    assert result.status.value == "CLASSIFICADO"
    assert result.classificacao.categoria == "ultraprocessado"
    assert result.classificacao.status.value == expected_status
    assert result.classificacao.justificativa
    assert result.classificacao.titulo
    assert result.classificacao.resumo
    assert result.classificacao.orientacao
    assert result.classificacao.aviso


def test_analysis_pipeline_enriches_response_with_evidences(monkeypatch):
    ocr = StubOCR("INGREDIENTES: aromatizante, corante e conservante.")
    monkeypatch.setattr(
        analysis_pipeline_module,
        "classificar",
        lambda texto: {
            "classificacao_final": "ultraprocessado",
            "regras": {
                "score": 7,
                "ingredientes_detectados": [
                    "aromatizante",
                    "corante",
                    "conservante",
                ],
            },
            "explicacao": "Texto tecnico antigo.",
        },
    )
    pipeline = AnalysisPipeline(ocr_service=ocr)

    result = pipeline.run(image_bytes=b"img")

    assert result.classificacao.status.value == "ALTO_INDICIO"
    assert result.classificacao.novaGrupo == 4
    assert result.classificacao.titulo == "Fortes indícios de ultraprocessamento"
    assert result.classificacao.evidencias[0].termo == "aromatizante"
    assert result.classificacao.ingredientesDetectados == [
        "aromatizante",
        "corante",
        "conservante",
    ]


def test_analysis_pipeline_returns_not_classified_when_ocr_has_no_text():
    pipeline = AnalysisPipeline(
        ocr_service=StubOCR(response_text=None),
    )

    result = pipeline.run(image_bytes=b"img")

    assert result.status.value == "NAO_CLASSIFICADO"
    assert result.classificacao.status.value == "BAIXO_INDICIO"
    assert result.classificacao.novaGrupo is None
    assert result.classificacao.evidencias == []


@pytest.mark.parametrize("texto", [
    "açúcar refinado",
    "sal refinado",
    "aromatizante",
])
def test_analysis_pipeline_does_not_classify_front_label_as_ingredient_list(texto):
    result = AnalysisPipeline(ocr_service=StubOCR(texto)).run(image_bytes=b"img")

    assert result.status.value == "NAO_CLASSIFICADO"
    assert result.classificacao.novaGrupo is None
    assert result.classificacao.evidencias == []


@pytest.mark.parametrize(
    "texto, grupo, status",
    [
        ("Ingredientes: açúcar refinado.", 2, "BAIXO_INDICIO"),
        ("Ingredientes: atum, água e sal.", 3, "MEDIO_INDICIO"),
        ("Ingredientes: água, açúcar, corante e aromatizante.", 4, "ALTO_INDICIO"),
    ],
)
def test_analysis_pipeline_maps_nova_groups_without_changing_contract(texto, grupo, status):
    result = AnalysisPipeline(ocr_service=StubOCR(texto)).run(image_bytes=b"img")
    payload = result.model_dump(mode="json")

    assert payload["status"] == "CLASSIFICADO"
    assert payload["classificacao"]["novaGrupo"] == grupo
    assert payload["classificacao"]["status"] == status
    assert set(payload["classificacao"]) == {
        "categoria", "status", "justificativa", "novaGrupo", "titulo", "resumo",
        "orientacao", "evidencias", "ingredientesDetectados", "aviso",
    }


@pytest.mark.parametrize("texto", [
    "leite pasteurizado sal e quimosina",
    "morango acucar pectina e suco de limao",
    "pepino vinagre agua acucar sal especiarias e aroma natural de endro",
    "agua feijao carioca oleo de girassol sal alho e louro",
])
def test_analysis_pipeline_classifies_group_3_without_ocr_punctuation(texto):
    result = AnalysisPipeline(ocr_service=StubOCR(texto)).run(image_bytes=b"img")

    assert result.status.value == "CLASSIFICADO"
    assert result.classificacao.novaGrupo == 3
    assert result.classificacao.status.value == "MEDIO_INDICIO"
