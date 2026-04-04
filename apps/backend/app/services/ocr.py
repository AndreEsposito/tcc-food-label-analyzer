import logging
import os
from abc import ABC, abstractmethod

from google.api_core.exceptions import DeadlineExceeded, GoogleAPICallError, RetryError
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import vision

from app.core.config import Settings
from app.services.exceptions import (
    OCRAuthenticationError,
    OCRNoTextError,
    OCRServiceError,
    OCRTimeoutError,
)

logger = logging.getLogger(__name__)


class OCRService(ABC):
    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> str:
        raise NotImplementedError


class GoogleVisionOCRService(OCRService):
    def __init__(self, settings: Settings):
        self._timeout_seconds = settings.google_vision_timeout_seconds
        if settings.google_application_credentials:
            os.environ.setdefault(
                "GOOGLE_APPLICATION_CREDENTIALS",
                settings.google_application_credentials,
            )
        self._client = vision.ImageAnnotatorClient()

    def extract_text(self, image_bytes: bytes) -> str:
        logger.debug(f"Iniciando extração de texto (tamanho: {len(image_bytes)} bytes)")
        
        if not image_bytes:
            logger.error("Imagem vazia recebida")
            raise OCRNoTextError("Imagem vazia.")

        image = vision.Image(content=image_bytes)
        try:
            logger.debug("Enviando requisição para Google Vision API...")
            response = self._client.text_detection(
                image=image,
                timeout=self._timeout_seconds,
            )
            logger.debug("Resposta recebida do Google Vision API")
        except DefaultCredentialsError as exc:
            logger.error(f"Erro de autenticação Google Vision: {exc}")
            raise OCRAuthenticationError(
                "Credenciais da Google Vision API nao configuradas corretamente."
            ) from exc
        except (DeadlineExceeded, RetryError) as exc:
            logger.error(f"Timeout na requisição Google Vision: {exc}")
            raise OCRTimeoutError("Timeout ao consultar a Google Vision API.") from exc
        except GoogleAPICallError as exc:
            logger.error(f"Erro na chamada Google Vision API: {exc}")
            raise OCRServiceError(f"Falha ao consultar a Google Vision API: {exc}") from exc

        if response.error.message:
            logger.error(f"Erro na resposta Google Vision: {response.error.message}")
            raise OCRServiceError(response.error.message)

        text = ""
        if response.full_text_annotation and response.full_text_annotation.text:
            text = response.full_text_annotation.text
            logger.debug("Texto extraído da anotação completa")
        elif response.text_annotations:
            text = response.text_annotations[0].description or ""
            logger.debug("Texto extraído da primeira anotação")

        text = text.strip()
        if not text:
            logger.warning("Google Vision não retornou texto")
            raise OCRNoTextError("Google Vision nao retornou texto.")
        
        logger.debug(f"Texto extraído do Google Vision: {text}")
        logger.info(f"Extração de texto concluída: {len(text)} caracteres")
        return text
