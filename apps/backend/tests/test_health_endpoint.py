from unittest.mock import Mock

from app.api.v1.deps import get_analysis_pipeline
from app.main import app
from app.services.ocr import GoogleVisionOCRService


def test_get_health_sem_executar_servicos(client, monkeypatch):
    pipeline = Mock(side_effect=AssertionError("Pipeline nao deve ser criado"))
    ocr = Mock(side_effect=AssertionError("OCR nao deve ser executado"))
    vision_client = Mock(side_effect=AssertionError("Google Vision nao deve ser chamado"))
    model = Mock(side_effect=AssertionError("Modelo nao deve ser carregado"))

    app.dependency_overrides[get_analysis_pipeline] = pipeline
    monkeypatch.setattr(GoogleVisionOCRService, "extract_text", ocr)
    monkeypatch.setattr("app.services.ocr.vision.ImageAnnotatorClient", vision_client)
    monkeypatch.setattr("app.main.carregar_modelo", model)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    pipeline.assert_not_called()
    ocr.assert_not_called()
    vision_client.assert_not_called()
    model.assert_not_called()
