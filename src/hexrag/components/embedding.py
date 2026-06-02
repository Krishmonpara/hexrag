"""Embedding component: builds one LlamaIndex `BaseEmbedding` from settings."""

from __future__ import annotations

import logging

from injector import inject, singleton
from llama_index.core.embeddings import BaseEmbedding, MockEmbedding

from hexrag.settings.models import Settings

logger = logging.getLogger(__name__)


@singleton
class EmbeddingComponent:
    embedding_model: BaseEmbedding

    @inject
    def __init__(self, settings: Settings) -> None:
        mode = settings.embedding.mode
        logger.info("Initializing embedding model in mode=%s", mode)
        match mode:
            case "mock":
                # Deterministic fake vectors of the configured dimension — lets the
                # full RAG pipeline run with no model download.
                self.embedding_model = MockEmbedding(embed_dim=settings.embedding.embed_dim)
            case "ollama":
                try:
                    from llama_index.embeddings.ollama import OllamaEmbedding
                except ImportError as e:
                    raise ImportError(
                        "Ollama deps not installed. Run: uv sync --extra ollama"
                    ) from e
                self.embedding_model = OllamaEmbedding(
                    model_name=settings.ollama.embedding_model,
                    base_url=settings.ollama.api_base,
                )
            case "openai":
                try:
                    from llama_index.embeddings.openai import OpenAIEmbedding
                except ImportError as e:
                    raise ImportError(
                        "OpenAI deps not installed. Run: uv sync --extra openai"
                    ) from e
                self.embedding_model = OpenAIEmbedding(
                    api_base=settings.openai.api_base,
                    api_key=settings.openai.api_key,
                    model=settings.openai.embedding_model,
                )
            case "huggingface":
                try:
                    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
                except ImportError as e:
                    raise ImportError(
                        "HuggingFace deps not installed. Run: uv sync --extra huggingface"
                    ) from e
                self.embedding_model = HuggingFaceEmbedding(
                    model_name=settings.huggingface.embedding_model_name,
                )
            case _:
                raise ValueError(f"Unsupported embedding.mode: {mode}")
