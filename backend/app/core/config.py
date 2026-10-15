from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None

    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    OPENAI_TIMEOUT_SECONDS: float = 30.0
    OPENAI_MAX_OUTPUT_TOKENS: int = 1000

    FRONTEND_ORIGIN: str

    LOG_LEVEL: str = "INFO"

    ALEMBIC_DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    AUTH_COOKIE_NAME: str = "access_token"
    AUTH_COOKIE_SECURE: bool = True
    AUTH_COOKIE_HTTPONLY: bool = True
    AUTH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    AUTH_COOKIE_PATH: str = "/"
    CSRF_TRUSTED_ORIGINS: str = ""

    OTEL_EXPORTER_OTLP_ENDPOINT: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = (
        "http://localhost:8000/auth/google/callback"
    )
    GOOGLE_OAUTH_COOKIE_SECURE: bool = True
    GOOGLE_OAUTH_STATE_MAX_AGE_SECONDS: int = 300
    GOOGLE_OAUTH_TIMEOUT_SECONDS: float = 10.0


settings = Settings()
