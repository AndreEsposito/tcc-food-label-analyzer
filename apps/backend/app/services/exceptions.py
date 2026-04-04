class OCRServiceError(Exception):
    """Erro base para falhas no provedor de OCR."""


class OCRAuthenticationError(OCRServiceError):
    """Falha de autenticacao com provedor OCR."""


class OCRTimeoutError(OCRServiceError):
    """Timeout na chamada ao provedor OCR."""


class OCRNoTextError(OCRServiceError):
    """OCR executou, mas sem texto util para processamento."""
