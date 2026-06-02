"""POST /v1/embeddings — OpenAI-compatible embeddings endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from hexrag.api.openai_schema import EmbeddingData, EmbeddingResponse
from hexrag.components.embedding import EmbeddingComponent

embeddings_router = APIRouter(prefix="/v1", tags=["Embeddings"])


class EmbeddingRequest(BaseModel):
    input: str | list[str]
    model: str = "hexrag"


@embeddings_router.post("/embeddings")
def embeddings(request: Request, body: EmbeddingRequest) -> EmbeddingResponse:
    component = request.state.injector.get(EmbeddingComponent)
    texts = [body.input] if isinstance(body.input, str) else body.input
    vectors = component.embedding_model.get_text_embedding_batch(texts)
    data = [EmbeddingData(index=i, embedding=v) for i, v in enumerate(vectors)]
    return EmbeddingResponse(data=data)
