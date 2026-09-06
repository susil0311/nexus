"""
NEXUS PM AI Service – Configuration
Uses pydantic-settings to load from environment / .env file.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Gemini ──────────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = ""

    # ── ChromaDB ────────────────────────────────────────────────────────────
    CHROMADB_PATH: str = "./chroma_data"

    # ── Embedding model ──────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── Mock mode (skip real AI calls) ──────────────────────────────────────
    MOCK_MODE: bool = False

    # ── Service port ─────────────────────────────────────────────────────────
    AI_SERVICE_PORT: int = 8001

    # ── Optional OpenAI key (fallback) ───────────────────────────────────────
    OPENAI_API_KEY: str = ""

    # ── Gemini model names ────────────────────────────────────────────────────
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_PRO_MODEL: str = "gemini-1.5-pro"

    # ── XGBoost model persistence path ───────────────────────────────────────
    MODEL_SAVE_PATH: str = "./models"


settings = Settings()
