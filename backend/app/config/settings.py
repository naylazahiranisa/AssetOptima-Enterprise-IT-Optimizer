"""Application configuration via Pydantic v2 Settings.

Single source of truth for all environment-driven configuration.
Supports explicit DATABASE_URL override or construction from
individual POSTGRES_* components.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application metadata
    APP_NAME: str = "AssetOptima"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Enterprise IT Asset & License Optimizer"

    # Security
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database — individual components
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "assetoptima"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    # Database — explicit URL override (takes priority if set)
    DATABASE_URL: str | None = None

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Connection pool
    POSTGRES_POOL_SIZE: int = 10
    POSTGRES_MAX_OVERFLOW: int = 20

    # External APIs
    OPENAI_API_KEY: str = ""

    # RAG / Vector Store
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_COLLECTION: str = "assetoptima"
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    RAG_TOP_K_DEFAULT: int = 5
    RAG_SCORE_THRESHOLD: float = 0.0

    # Document management
    UPLOAD_MAX_SIZE_MB: int = 10
    UPLOAD_ALLOWED_EXTENSIONS: str = ".pdf,.docx,.txt,.csv,.md"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def database_url(self) -> str:
        """Return the effective async database URL."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        """Synchronous variant for Alembic migrations."""
        return self.database_url.replace("+asyncpg", "+psycopg2")

    @property
    def log_level_int(self) -> int:
        import logging
        return getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)


settings = Settings()
