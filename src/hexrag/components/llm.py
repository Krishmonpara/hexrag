"""LLM component: builds one LlamaIndex `LLM` from settings.

Every backend satisfies the `LLM` interface, so services depend on this single
typed attribute and never on a concrete provider. Add a backend by adding a
branch here and a `mode` to LLMSettings."""

from __future__ import annotations

import logging

from injector import inject, singleton
from llama_index.core.llms import LLM, MockLLM

from hexrag.settings.models import Settings

logger = logging.getLogger(__name__)


@singleton
class LLMComponent:
    llm: LLM

    @inject
    def __init__(self, settings: Settings) -> None:
        mode = settings.llm.mode
        logger.info("Initializing LLM in mode=%s", mode)
        match mode:
            case "mock":
                self.llm = MockLLM()
            case "ollama":
                try:
                    from llama_index.llms.ollama import Ollama
                except ImportError as e:
                    raise ImportError(
                        "Ollama deps not installed. Run: uv sync --extra ollama"
                    ) from e
                o = settings.ollama
                self.llm = Ollama(
                    model=o.llm_model,
                    base_url=o.api_base,
                    temperature=settings.llm.temperature,
                    context_window=settings.llm.context_window,
                    request_timeout=o.request_timeout,
                )
            case "openai":
                try:
                    from llama_index.llms.openai import OpenAI
                except ImportError as e:
                    raise ImportError(
                        "OpenAI deps not installed. Run: uv sync --extra openai"
                    ) from e
                oa = settings.openai
                self.llm = OpenAI(
                    api_base=oa.api_base,
                    api_key=oa.api_key,
                    model=oa.model,
                    temperature=settings.llm.temperature,
                    max_tokens=settings.llm.max_new_tokens,
                )
            case _:
                raise ValueError(f"Unsupported llm.mode: {mode}")
