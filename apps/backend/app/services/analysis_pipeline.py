import logging
from uuid import uuid4

from app.models.schemas import (
    AnalysisResponse,
    AnalysisStatus,
    ClassificationResult,
    ClassificationStatus,
)
from app.services.ocr import OCRService
from packages.classification_core.pipeline import classificar

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    def __init__(self, ocr_service: OCRService):
        self._ocr_service = ocr_service

    def run(self, image_bytes: bytes) -> AnalysisResponse:
        logger.debug(f"Pipeline iniciado com imagem de {len(image_bytes)} bytes")

        logger.debug("Etapa 1: Extraindo texto com OCR...")
        raw_text = self._ocr_service.extract_text(image_bytes)
        logger.debug(f"OCR concluído: {len(raw_text)} caracteres extraídos")

        logger.debug("Etapa 2: Classificando produto com classification_core...")
        core_result = classificar(raw_text)
        classification = self._build_classification_result(core_result)
        logger.info(
            "Classificação final: %s - %s",
            classification.status,
            classification.categoria,
        )

        analysis_id = uuid4()
        logger.info(f"Análise {analysis_id} concluída com sucesso")
        return AnalysisResponse(
            analiseId=analysis_id,
            status=AnalysisStatus.CLASSIFICADO,
            classificacao=classification,
        )

    def _build_classification_result(self, core_result: dict) -> ClassificationResult:
        classificacao_final = core_result.get("classificacao_final", "")
        explicacao = core_result.get("explicacao", "")

        try:
            if classificacao_final == "ultraprocessado":
                status = ClassificationStatus.ALTO_INDICIO
            elif classificacao_final == "processado":
                status = ClassificationStatus.MEDIO_INDICIO
            else:
                status = ClassificationStatus.BAIXO_INDICIO
        except Exception as exc:
            logger.error(f"Erro ao determinar status de classificação: {exc}")
            raise Exception(
            status_code=status.HTTP_500_BAD_GATEWAY,
            detail="Falha ao classificar rótulos.",
        )

        return ClassificationResult(
            categoria=classificacao_final or "desconhecido",
            status=status,
            justificativa=explicacao
            or "Nao foi possivel gerar uma explicacao para a classificacao.",
        )
