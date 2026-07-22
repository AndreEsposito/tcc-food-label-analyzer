from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    CLASSIFICADO = "CLASSIFICADO"
    NAO_CLASSIFICADO = "NAO_CLASSIFICADO"


class ClassificationStatus(str, Enum):
    BAIXO_INDICIO = "BAIXO_INDICIO"
    MEDIO_INDICIO = "MEDIO_INDICIO"
    ALTO_INDICIO = "ALTO_INDICIO"


class EvidenceItem(BaseModel):
    termo: str
    tipo: str
    descricao: str


class ClassificationResult(BaseModel):
    categoria: str = Field(default="ultraprocessado")
    status: ClassificationStatus
    justificativa: str
    novaGrupo: int | None = Field(default=None, ge=2, le=4)
    titulo: str = Field(default="")
    resumo: str = Field(default="")
    orientacao: str = Field(default="")
    evidencias: list[EvidenceItem] = Field(default_factory=list)
    ingredientesDetectados: list[str] = Field(default_factory=list)
    aviso: str = Field(
        default=(
            "Resultado informativo baseado na lista de ingredientes identificada pelo OCR. "
            "Esta análise não substitui a avaliação de um profissional de nutrição."
        )
    )


class AnalysisResponse(BaseModel):
    analiseId: UUID
    status: AnalysisStatus
    classificacao: ClassificationResult
