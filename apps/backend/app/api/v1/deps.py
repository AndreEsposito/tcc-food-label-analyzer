from functools import lru_cache

from app.core.config import get_settings
from app.services.analysis_pipeline import AnalysisPipeline
from app.services.ocr import GoogleVisionOCRService


@lru_cache
def get_analysis_pipeline() -> AnalysisPipeline:
    settings = get_settings()
    return AnalysisPipeline(
        ocr_service=GoogleVisionOCRService(settings=settings),
    )
