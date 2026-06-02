"""OpenAI-compatible request/response models, so standard OpenAI clients work.

Mirrors the shapes at https://platform.openai.com/docs/api-reference/chat for
chat/completions, plus the embeddings object. `sources` is a hexrag extension on
each choice (ignored by standard clients) carrying the retrieved RAG chunks."""

from __future__ import annotations

import time
import uuid
from collections.abc import Iterator
from typing import Literal

from pydantic import BaseModel, Field

from hexrag.services.chat import Source

MODEL_NAME = "hexrag"


class ChatCompletionMessage(BaseModel):
    role: Literal["system", "user", "assistant"] = "user"
    content: str | None = None


class Delta(BaseModel):
    content: str | None = None


class Choice(BaseModel):
    index: int = 0
    finish_reason: str | None = None
    message: ChatCompletionMessage | None = None
    delta: Delta | None = None
    sources: list[Source] | None = None


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletion(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}")
    object: Literal["chat.completion", "chat.completion.chunk"] = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = MODEL_NAME
    choices: list[Choice]
    usage: Usage = Usage()


def completion_from_text(text: str, sources: list[Source] | None = None) -> ChatCompletion:
    return ChatCompletion(
        choices=[
            Choice(
                finish_reason="stop",
                message=ChatCompletionMessage(role="assistant", content=text),
                sources=sources,
            )
        ]
    )


def _chunk_json(text: str | None, finish_reason: str | None = None) -> str:
    chunk = ChatCompletion(
        object="chat.completion.chunk",
        choices=[Choice(delta=Delta(content=text), finish_reason=finish_reason)],
    )
    return chunk.model_dump_json()


def to_sse_stream(tokens: Iterator[str]) -> Iterator[str]:
    """Server-sent-events stream matching OpenAI's streaming chunk format."""
    for token in tokens:
        yield f"data: {_chunk_json(token)}\n\n"
    yield f"data: {_chunk_json(None, finish_reason='stop')}\n\n"
    yield "data: [DONE]\n\n"


# ---- Embeddings ----


class EmbeddingData(BaseModel):
    object: Literal["embedding"] = "embedding"
    index: int
    embedding: list[float]


class EmbeddingResponse(BaseModel):
    object: Literal["list"] = "list"
    model: str = MODEL_NAME
    data: list[EmbeddingData]
    usage: Usage = Usage()
