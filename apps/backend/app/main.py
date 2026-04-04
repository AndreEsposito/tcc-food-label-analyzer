import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    logger.info(f"Inicializando aplicação {settings.app_name} v0.1.0 (debug={settings.debug})")
    app = FastAPI(
        title=settings.app_name,
        description="API para analise de rotulos alimentares",
        version="0.1.0",
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
