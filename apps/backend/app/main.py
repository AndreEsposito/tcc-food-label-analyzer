import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from packages.classification_core.ml import MODEL_PATH, carregar_modelo

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        carregar_modelo()
        logger.info("Modelo de ML carregado com sucesso: %s", MODEL_PATH)
    except Exception as exc:
        logger.exception(
            "Falha ao carregar modelo de ML no startup (%s): %s",
            MODEL_PATH,
            exc,
        )
        raise RuntimeError(
            f"Nao foi possivel carregar o modelo de ML em {MODEL_PATH}."
        ) from exc

    yield


def create_app() -> FastAPI:
    settings = get_settings()
    logger.info(f"Inicializando aplicação {settings.app_name} v0.1.0 (debug={settings.debug})")
    app = FastAPI(
        title=settings.app_name,
        description="API para analise de rotulos alimentares",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    logger.info("Middlewares e rotas configurados com sucesso")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    logger.info("Iniciando servidor FastAPI em http://localhost:8000")
    uvicorn.run(app, host="localhost", port=8000)
