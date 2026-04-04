import logging
from uuid import uuid4

from app.models.schemas import AnalysisResponse, AnalysisStatus
from app.services.classification import Classifier
from app.services.ocr import OCRService
from app.services.text_preprocessing import TextPreprocessor

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    def __init__(
        self,
        ocr_service: OCRService,
        text_preprocessor: TextPreprocessor,
        classifier: Classifier,
    ):
        self._ocr_service = ocr_service
        self._text_preprocessor = text_preprocessor
        self._classifier = classifier

    def run(self, image_bytes: bytes) -> AnalysisResponse:
        logger.debug(f"Pipeline iniciado com imagem de {len(image_bytes)} bytes")
        
        logger.debug("Etapa 1: Extraindo texto com OCR...")
        raw_text = self._ocr_service.extract_text(image_bytes)
        logger.debug(f"OCR concluído: {len(raw_text)} caracteres extraídos")
        
        logger.debug("Etapa 2: Pré-processando texto...")
        ingredients = self._text_preprocessor.extract_ingredients(raw_text)
        logger.info(f"Ingredientes extraídos: {len(ingredients)} itens")
        
        logger.debug("Etapa 3: Classificando produto...")
        classification = self._classifier.classify(ingredients)
        logger.info(f"Classificação: {classification.status} - {classification.categoria}")

        analysis_id = uuid4()
        logger.info(f"Análise {analysis_id} concluída com sucesso")
        return AnalysisResponse(
            analiseId=analysis_id,
            status=AnalysisStatus.CLASSIFICADO,
            classificacao=classification,
        )
