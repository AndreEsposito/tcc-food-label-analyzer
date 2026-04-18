import base64
import json
import os
import tempfile
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


def _get_env_file() -> str:
    """
    Detecta o ambiente e retorna o arquivo .env apropriado.

    Ordem de prioridade:
    1. Variavel de ambiente APP_ENV -> usa .env.{APP_ENV}
    2. Arquivo .env.local se existir
    3. Arquivo .env.production se existir
    4. Padrao: .env.local (development)
    """
    app_env = os.getenv("APP_ENV", "").lower()

    candidates: list[Path] = []
    if app_env:
        candidates.append(BASE_DIR / f".env.{app_env}")

    candidates.extend(
        [
            BASE_DIR / ".env.local",
            BASE_DIR / ".env.production",
            Path.cwd() / ".env.local",
            Path.cwd() / ".env.production",
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return str(BASE_DIR / ".env.local")


def _resolve_backend_path(path_value: str) -> str:
    path = Path(path_value)
    if path.is_absolute():
        return str(path)
    return str((BASE_DIR / path).resolve())


class Settings(BaseSettings):
    app_name: str = "Food Label Analyzer API"
    debug: bool = False
    google_application_credentials: str | None = None
    google_credentials_json: str | None = None
    google_vision_timeout_seconds: float = 10.0
    app_env: str | None = None

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

    @field_validator("google_application_credentials", mode="before")
    @classmethod
    def normalize_google_credentials_path(cls, value):
        if not value:
            return value
        return _resolve_backend_path(value)

    @field_validator("google_credentials_json", mode="after")
    @classmethod
    def setup_google_credentials(cls, value):
        """
        Processa credenciais do Google a partir de variavel de ambiente.
        Suporta dois formatos:
        1. JSON direto como string
        2. Base64 do JSON
        """
        if not value:
            return value

        try:
            decoded = base64.b64decode(value).decode("utf-8")
            credentials_dict = json.loads(decoded)
        except Exception:
            try:
                credentials_dict = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError("google_credentials_json deve ser JSON valido ou base64 de JSON") from exc

        temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
        )
        json.dump(credentials_dict, temp_file)
        temp_file.close()

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file.name

        return temp_file.name


@lru_cache
def get_settings() -> Settings:
    return Settings()
