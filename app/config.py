from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is installed in normal use
    load_dotenv = None


ROOT_DIR = Path(__file__).resolve().parent.parent

if load_dotenv is not None:
    load_dotenv(ROOT_DIR / ".env")


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    root_dir: Path = ROOT_DIR
    app_name: str = "NXP AIoT Cloud 智能客服系统"
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    llm_model: str = os.getenv("LLM_MODEL", "qwen2.5:7b")
    embed_model: str = os.getenv("EMBED_MODEL", "nomic-embed-text")
    embed_provider: str = os.getenv("EMBED_PROVIDER", "ollama").lower()
    vector_store: str = os.getenv("VECTOR_STORE", "chroma").lower()
    top_k: int = _int_env("TOP_K", 3)
    min_score: float = _float_env("MIN_SCORE", 0.1)
    chunk_size: int = _int_env("CHUNK_SIZE", 500)
    chunk_overlap: int = _int_env("CHUNK_OVERLAP", 80)
    mock_llm: bool = _bool_env("MOCK_LLM", False)
    temperature: float = _float_env("TEMPERATURE", 0.2)
    request_timeout: int = _int_env("REQUEST_TIMEOUT", 120)

    @property
    def data_dir(self) -> Path:
        return self.root_dir / "data"

    @property
    def knowledge_base_dir(self) -> Path:
        return self.data_dir / "knowledge_base"

    @property
    def vector_store_dir(self) -> Path:
        return self.data_dir / "vector_store"

    @property
    def frontend_dir(self) -> Path:
        return self.root_dir / "frontend"


def get_settings() -> Settings:
    settings = Settings()
    settings.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
    settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
