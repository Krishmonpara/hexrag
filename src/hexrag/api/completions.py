"""POST /v1/completions — legacy text-completion shape, delegates to chat."""

from __future__ import annotations

from fastapi import APIRouter, Request
from llama_index.core.llms import ChatMessage, MessageRole
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from hexrag.api.openai_schema import ChatCompletion, completion_from_text, to_sse_stream
from hexrag.services.chat import ChatService

completions_router = APIRouter(prefix="/v1", tags=["Completions"])


class CompletionRequest(BaseModel):
    prompt: str
    model: str = "hexrag"
    stream: bool = False
    use_context: bool = True
    doc_ids: list[str] | None = None


@completions_router.post("/completions", response_model=None)
def completions(
    request: Request, body: CompletionRequest
) -> ChatCompletion | StreamingResponse:
    service = request.state.injector.get(ChatService)
    messages = [ChatMessage(role=MessageRole.USER, content=body.prompt)]

    if body.stream:
        gen = service.stream_chat(messages, use_context=body.use_context, doc_ids=body.doc_ids)
        return StreamingResponse(to_sse_stream(gen.response), media_type="text/event-stream")

    completion = service.chat(messages, use_context=body.use_context, doc_ids=body.doc_ids)
    return completion_from_text(completion.response, sources=completion.sources)
