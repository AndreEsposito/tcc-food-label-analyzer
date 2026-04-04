import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.v1.deps import get_analysis_pipeline

logger = logging.getLogger(__name__)
from app.models.schemas import AnalysisResponse
from app.services.analysis_pipeline import AnalysisPipeline
from app.services.exceptions import (
    OCRAuthenticationError,
    OCRNoTextError,
    OCRServiceError,
    OCRTimeoutError,
)

router = APIRouter(tags=["analises"])


@router.post("/analises", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def criar_analise(
    imagem: UploadFile = File(...),
    pipeline: AnalysisPipeline = Depends(get_analysis_pipeline),
) -> AnalysisResponse:
    logger.info(f"Recebido upload: {imagem.filename} (content_type={imagem.content_type})")
    
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    file_extension = None
    if imagem.filename:
        file_extension = "." + imagem.filename.rsplit(".", 1)[-1].lower()
    
    is_valid = (
        (imagem.content_type and imagem.content_type.startswith("image/"))
        or file_extension in valid_extensions
    )
    
    if not is_valid:
        logger.warning(f"Arquivo inválido: {imagem.filename} (tipo={imagem.content_type})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O campo 'imagem' deve conter um arquivo de imagem. Recebido: {imagem.content_type}",
        )

    image_bytes = await imagem.read()
    logger.debug(f"Imagem lida: {len(image_bytes)} bytes")
    
    if not image_bytes:
        logger.error(f"Imagem vazia: {imagem.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo de imagem vazio.",
        )

    try:
        logger.info(f"Iniciando pipeline para {imagem.filename}")
        result = pipeline.run(image_bytes=image_bytes)
        logger.info(f"Sucesso: {result.analiseId} - {result.classificacao.status}")
        return result
    except OCRAuthenticationError as exc:
        logger.error(f"Erro autenticação OCR: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Falha de autenticacao no provedor OCR.",
        ) from exc
    except OCRTimeoutError as exc:
        logger.error(f"Timeout OCR: {exc}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timeout no servico OCR.",
        ) from exc
    except OCRNoTextError as exc:
        logger.warning(f"Sem texto extraído: {exc}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nao foi possivel extrair texto da imagem.",
        ) from exc
    except OCRServiceError as exc:
        logger.error(f"Erro OCR: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Falha ao processar OCR.",
        ) from exc
