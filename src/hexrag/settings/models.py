"""Typed settings tree. Each component reads its own slice and `mode`/`database`
string to decide which concrete implementation to build."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from hexrag.settings.loader import load_active_settings


class CorsSettings(BaseModel):
    enabled: bool = False
    allow_origins: list[str] = ["*"]
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]


class ServerSettings(BaseModel):
    env_name: str = "local"
    host: str = "0.0.0.0"
    port: int = 8001
    cors: CorsSettings = CorsSettings()


class LLMSettings(BaseModel):
    mode: Literal["mock", "ollama", "openai"] = "mock"
    system_prompt: str = (
        "You are a helpful assistant. Answer using the provided context when available. "
        "If the context does not contain the answer, say you don't know."
    )
    temperature: float = 0.1
    max_new_tokens: int = 512
    context_window: int = 8192


class EmbeddingSettings(BaseModel):
    mode: Literal["mock", "ollama", "openai", "huggingface"] = "mock"
    embed_dim: int = 384


class VectorStoreSettings(BaseModel):
    database: Literal["simple", "chroma"] = "simple"


class RagSettings(BaseModel):
    similarity_top_k: int = 3


class OllamaSettings(BaseModel):
    api_base: str = "http://localhost:11434"
    llm_model: str = "llama3.2"
    embedding_model: str = "nomic-embed-text"
    request_timeout: float = 120.0


class OpenAISettings(BaseModel):
    api_base: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"


class HuggingFaceSettings(BaseModel):
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"


class UISettings(BaseModel):
    enabled: bool = False
    path: str = "/ui"


class Settings(BaseModel):
    server: ServerSettings = ServerSettings()
    cors: CorsSettings = CorsSettings()
    llm: LLMSettings = LLMSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
    vectorstore: VectorStoreSettings = VectorStoreSettings()
    rag: RagSettings = RagSettings()
    ollama: OllamaSettings = OllamaSettings()
    openai: OpenAISettings = OpenAISettings()
    huggingface: HuggingFaceSettings = HuggingFaceSettings()
    ui: UISettings = UISettings()


# Eagerly-loaded settings, used for DI binding. Prefer injecting `Settings`
# (or calling `settings()`) over importing this directly.
unsafe_typed_settings = Settings(**load_active_settings())


def settings() -> Settings:
    """Fetch the active settings from the DI container."""
    from hexrag.di import global_injector

    return global_injector.get(Settings)
