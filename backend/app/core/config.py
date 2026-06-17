from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "WorkLog AI"
    app_env: str = "development"
    app_debug: bool = False
    app_base_url: str = "http://localhost"
    app_secret_key: str = "change-me"

    database_url: str = "postgresql+psycopg://worklog:worklog@localhost:5432/worklog"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-me-jwt"
    jwt_expire_minutes: int = 1440

    upload_driver: str = "local"
    upload_dir: str = "/app/uploads"
    export_dir: str = "/app/exports"
    max_upload_size_mb: int = 50

    ai_enable: bool = True
    ai_default_provider: str = "openai_compatible"
    ai_request_timeout: int = 60
    ai_desensitization_default: bool = True

    config_encryption_key: str = "please-change-this-32-byte-key"
    cors_origins: str = "http://localhost,http://127.0.0.1"

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
