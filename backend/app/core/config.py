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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()