import pytest

from app.services.analysis_pipeline import AnalysisPipeline
from app.services.classification import MockRuleBasedClassifier
from app.services.exceptions import OCRNoTextError
from app.services.text_preprocessing import TextPreprocessor


class StubOCR:
    def __init__(self, response_text: str | None):
        self.response_text = response_text

    def extract_text(self, image_bytes: bytes) -> str:
        if self.response_text is None:
            raise OCRNoTextError("sem texto")
        return self.response_text


def test_analysis_pipeline_orchestrates_end_to_end():
    ocr = StubOCR(
        "INGREDIENTES: acucar, farinha de trigo, aromatizante, corante. ALERGICOS: contem gluten."
    )
    pipeline = AnalysisPipeline(
        ocr_service=ocr,
        text_preprocessor=TextPreprocessor(),
        classifier=MockRuleBasedClassifier(),
    )

    result = pipeline.run(image_bytes=b"img")

    assert result.status.value == "CLASSIFICADO"
    assert result.classificacao.categoria == "ultraprocessado"
    assert result.classificacao.status.value == "ALTO_INDICIO"


def test_analysis_pipeline_raises_when_ocr_fails():
    pipeline = AnalysisPipeline(
        ocr_service=StubOCR(response_text=None),
        text_preprocessor=TextPreprocessor(),
        classifier=MockRuleBasedClassifier(),
    )

    with pytest.raises(OCRNoTextError):
        pipeline.run(image_bytes=b"img")
