from functools import lru_cache

from app.core.config import get_settings
from app.services.analysis_pipeline import AnalysisPipeline
from app.services.classification import MockRuleBasedClassifier
from app.services.ocr import GoogleVisionOCRService
from app.services.text_preprocessing import TextPreprocessor


@lru_cache
def get_analysis_pipeline() -> AnalysisPipeline:
    settings = get_settings()
    return AnalysisPipeline(
        ocr_service=GoogleVisionOCRService(settings=settings),
        text_preprocessor=TextPreprocessor(),
        classifier=MockRuleBasedClassifier(),
    )
