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


def test_analysis_pipeline_raises_when_ocr_fails():
    pipeline = AnalysisPipeline(
        ocr_service=StubOCR(response_text=None),
    )

    with pytest.raises(OCRNoTextError):
        pipeline.run(image_bytes=b"img")
