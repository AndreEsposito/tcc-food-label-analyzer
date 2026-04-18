from uuid import UUID

from app.api.v1.deps import get_analysis_pipeline
from app.models.schemas import AnalysisResponse, AnalysisStatus, ClassificationResult, ClassificationStatus
from app.services.exceptions import OCRNoTextError
from app.main import app


class StubPipelineAltoIndicio:
    def run(self, image_bytes: bytes) -> AnalysisResponse:
        assert image_bytes == b"fake-image-bytes"
        return AnalysisResponse(
            analiseId=UUID("11111111-1111-1111-1111-111111111111"),
            status=AnalysisStatus.CLASSIFICADO,
            classificacao=ClassificationResult(
                categoria="ultraprocessado",
                status=ClassificationStatus.ALTO_INDICIO,
                justificativa="Foram identificados ingredientes associados a ultraprocessamento, como aromatizante e corante.",
            ),
        )


class StubPipelineMedioIndicio:
    def run(self, image_bytes: bytes) -> AnalysisResponse:
        assert image_bytes == b"fake-image-bytes"
        return AnalysisResponse(
            analiseId=UUID("22222222-2222-2222-2222-222222222222"),
            status=AnalysisStatus.CLASSIFICADO,
            classificacao=ClassificationResult(
                categoria="ultraprocessado",
                status=ClassificationStatus.MEDIO_INDICIO,
                justificativa="O produto contém alguns ingredientes que podem indicar processamento moderado, como açúcares adicionados.",
            ),
        )


class StubPipelineBaixoIndicio:
    def run(self, image_bytes: bytes) -> AnalysisResponse:
        assert image_bytes == b"fake-image-bytes"
        return AnalysisResponse(
            analiseId=UUID("33333333-3333-3333-3333-333333333333"),
            status=AnalysisStatus.CLASSIFICADO,
            classificacao=ClassificationResult(
                categoria="ultraprocessado",
                status=ClassificationStatus.BAIXO_INDICIO,
                justificativa="O produto apresenta indícios mínimos de ultraprocessamento com base na lista de ingredientes.",
            ),
        )


class FailingPipeline:
    def run(self, image_bytes: bytes) -> AnalysisResponse:
        raise OCRNoTextError("sem texto")


def test_post_analises_sucesso_alto_indicio(client):
    app.dependency_overrides[get_analysis_pipeline] = lambda: StubPipelineAltoIndicio()
    response = client.post(
        "/analises",
        files={"imagem": ("rotulo.jpg", b"fake-image-bytes", "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CLASSIFICADO"
    assert body["classificacao"]["categoria"] == "ultraprocessado"
    assert body["classificacao"]["status"] == "ALTO_INDICIO"


def test_post_analises_sucesso_medio_indicio(client):
    app.dependency_overrides[get_analysis_pipeline] = lambda: StubPipelineMedioIndicio()
    response = client.post(
        "/analises",
        files={"imagem": ("rotulo.jpg", b"fake-image-bytes", "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CLASSIFICADO"
    assert body["classificacao"]["categoria"] == "ultraprocessado"
    assert body["classificacao"]["status"] == "MEDIO_INDICIO"


def test_post_analises_sucesso_baixo_indicio(client):
    app.dependency_overrides[get_analysis_pipeline] = lambda: StubPipelineBaixoIndicio()
    response = client.post(
        "/analises",
        files={"imagem": ("rotulo.jpg", b"fake-image-bytes", "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CLASSIFICADO"
    assert body["classificacao"]["categoria"] == "ultraprocessado"
    assert body["classificacao"]["status"] == "BAIXO_INDICIO"


def test_post_analises_rejeita_arquivo_nao_imagem(client):
    app.dependency_overrides[get_analysis_pipeline] = lambda: StubPipelineAltoIndicio()
    response = client.post(
        "/analises",
        files={"imagem": ("rotulo.txt", b"texto", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "O campo 'imagem' deve conter um arquivo de imagem. Recebido: text/plain"


def test_post_analises_quando_ocr_sem_texto(client):
    app.dependency_overrides[get_analysis_pipeline] = lambda: FailingPipeline()
    response = client.post(
        "/analises",
        files={"imagem": ("rotulo.jpg", b"fake-image-bytes", "image/jpeg")},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Nao foi possivel extrair texto da imagem."
