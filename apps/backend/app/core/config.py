import json
import os
import tempfile
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_env_file() -> str:
    """
    Detecta o ambiente e retorna o arquivo .env apropriado.
    
    Ordem de prioridade:
    1. Variável de ambiente APP_ENV → usa .env.{APP_ENV}
    2. Arquivo .env.local se existir
    3. Arquivo .env.production se existir
    4. Padrão: .env.local (development)
    """
    app_env = os.getenv("APP_ENV", "").lower()
    
    if app_env:
        return f".env.{app_env}"
    
    # Detecção automática
    if Path(".env.local").exists():
        return ".env.local"
    elif Path(".env.production").exists():
        return ".env.production"
    
    # Padrão para desenvolvimento
    return ".env.local"


class Settings(BaseSettings):
    app_name: str = "Food Label Analyzer API"
    debug: bool = False
    google_application_credentials: str | None = None
    google_credentials_json: str | None = None  # JSON string ou base64 das credenciais
    google_vision_timeout_seconds: float = 10.0
    app_env: str | None = None  # Ambiente (local, production, etc)

    model_config = SettingsConfigDict(
        env_file=_get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"1", "true", "yes", "on", "dev", "development"}:
                return True
            if lowered in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        return False

    @field_validator("google_credentials_json", mode="after")
    @classmethod
    def setup_google_credentials(cls, value):
        """
        Processa credenciais do Google a partir de variável de ambiente.
        Suporta dois formatos:
        1. JSON direto como string
        2. Base64 do JSON (útil para variáveis de ambiente)
        """
        if not value:
            return value

        # Tenta decodificar como base64 se necessário
        try:
            import base64
            decoded = base64.b64decode(value).decode("utf-8")
            credentials_dict = json.loads(decoded)
        except Exception:
            # Se falhar, assume que é JSON direto
            try:
                credentials_dict = json.loads(value)
            except json.JSONDecodeError:
                raise ValueError("google_credentials_json deve ser JSON válido ou base64 de JSON")

        # Cria arquivo temporário com as credenciais
        temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
        )
        json.dump(credentials_dict, temp_file)
        temp_file.close()

        # Define variável de ambiente
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file.name

        return temp_file.name


@lru_cache
def get_settings() -> Settings:
    return Settings()
