from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nexuspm"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI / Gemini
    GEMINI_API_KEY: str = ""
    AI_SERVICE_URL: str = "http://localhost:8001"
    MOCK_AI_MODE: bool = True

    # Security
    JWT_SECRET: str = "change-me-in-production-super-secret-key-at-least-32-chars"
    JWT_EXPIRY_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"

    # ChromaDB
    CHROMADB_PATH: str = "./chromadb_data"

    # App meta
    PROJECT_NAME: str = "NEXUS PM"
    VERSION: str = "1.0.0"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]


settings = Settings()
