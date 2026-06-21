import logging
from dataclasses import dataclass
from typing import Mapping
from uuid import uuid4

from app.models.schemas import (
    AnalysisResponse,
    AnalysisStatus,
    ClassificationResult,
    ClassificationStatus,
)
from app.services.ocr import OCRService
from packages.classification_core.explanation_generator import gerar_explicacao_amigavel
from packages.classification_core.pipeline import classificar

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClassificationDomain:
    categoria: str
    status_by_core_classification: Mapping[str, ClassificationStatus]
    default_status: ClassificationStatus


ULTRAPROCESSING_DOMAIN = ClassificationDomain(
    categoria="ultraprocessado",
    status_by_core_classification={
        "ultraprocessado": ClassificationStatus.ALTO_INDICIO,
        "processado": ClassificationStatus.MEDIO_INDICIO,
        "pouco processado": ClassificationStatus.BAIXO_INDICIO,
    },
    default_status=ClassificationStatus.BAIXO_INDICIO,
)


class AnalysisPipeline:
    def __init__(
        self,
        ocr_service: OCRService,
        classification_domain: ClassificationDomain = ULTRAPROCESSING_DOMAIN,
    ):
        self._ocr_service = ocr_service
        self._classification_domain = classification_domain

    def run(self, image_bytes: bytes) -> AnalysisResponse:
        logger.debug(f"Pipeline iniciado com imagem de {len(image_bytes)} bytes")

        logger.debug("Etapa 1: Extraindo texto com OCR...")
        raw_text = self._ocr_service.extract_text(image_bytes)
        logger.debug(f"OCR concluido: {len(raw_text)} caracteres extraidos")

        logger.debug("Etapa 2: Classificando produto com classification_core...")
        core_result = classificar(raw_text)
        classification = self._build_classification_result(core_result)
        logger.info(
            "Classificacao final: %s - %s",
            classification.status,
            classification.categoria,
        )

        analysis_id = uuid4()
        logger.info(f"Analise {analysis_id} concluida com sucesso")
        return AnalysisResponse(
            analiseId=analysis_id,
            status=AnalysisStatus.CLASSIFICADO,
            classificacao=classification,
        )

    def _build_classification_result(self, core_result: dict) -> ClassificationResult:
        classificacao_final = core_result.get("classificacao_final", "")

        status = self._classification_domain.status_by_core_classification.get(
            classificacao_final,
            self._classification_domain.default_status,
        )
        explicacao_amigavel = self._build_friendly_explanation(
            core_result=core_result,
            classificacao_final=classificacao_final,
            status=status,
        )
        justificativa = (
            explicacao_amigavel.get("justificativa")
            or core_result.get("explicacao")
            or "Nao foi possivel gerar uma explicacao para a classificacao."
        )

        return ClassificationResult(
            categoria=self._classification_domain.categoria,
            status=status,
            justificativa=justificativa,
            novaGrupo=explicacao_amigavel.get("novaGrupo", 1),
            titulo=explicacao_amigavel.get("titulo", ""),
            resumo=explicacao_amigavel.get("resumo", ""),
            orientacao=explicacao_amigavel.get("orientacao", ""),
            evidencias=explicacao_amigavel.get("evidencias", []),
            ingredientesDetectados=explicacao_amigavel.get(
                "ingredientesDetectados",
                [],
            ),
            aviso=explicacao_amigavel.get("aviso", ""),
        )

    def _build_friendly_explanation(
        self,
        core_result: dict,
        classificacao_final: str,
        status: ClassificationStatus,
    ) -> dict:
        regras = core_result.get("regras", {})
        ingredientes_detectados = (
            core_result.get("ingredientes_detectados")
            or regras.get("ingredientes_detectados")
            or []
        )

        fallback = gerar_explicacao_amigavel(
            classificacao=classificacao_final,
            status=status.value,
            ingredientes_detectados=ingredientes_detectados,
            score=regras.get("score"),
        )
        explicacao_amigavel = core_result.get("explicacao_amigavel")
        if not isinstance(explicacao_amigavel, dict):
            return fallback

        return {
            key: explicacao_amigavel.get(key) or fallback_value
            for key, fallback_value in fallback.items()
        }
