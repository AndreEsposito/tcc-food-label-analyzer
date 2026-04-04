from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    CLASSIFICADO = "CLASSIFICADO"


class ClassificationStatus(str, Enum):
    BAIXO_INDICIO = "BAIXO_INDICIO"
    MEDIO_INDICIO = "MEDIO_INDICIO"
    ALTO_INDICIO = "ALTO_INDICIO"


class ClassificationResult(BaseModel):
    categoria: str = Field(default="ultraprocessado")
    status: ClassificationStatus
    justificativa: str


class AnalysisResponse(BaseModel):
    analiseId: UUID
    status: AnalysisStatus
    classificacao: ClassificationResult
