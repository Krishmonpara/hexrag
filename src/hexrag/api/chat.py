"""POST /v1/chat/completions — OpenAI-compatible chat endpoint with optional RAG."""

from __future__ import annotations

from fastapi import APIRouter, Request
from llama_index.core.llms import ChatMessage, MessageRole
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from hexrag.api.openai_schema import ChatCompletion, completion_from_text, to_sse_stream
from hexrag.services.chat import ChatService

chat_router = APIRouter(prefix="/v1", tags=["Chat"])


class ChatCompletionRequest(BaseModel):
    messages: list[dict]
    model: str = "hexrag"
    stream: bool = False
    # hexrag extensions (ignored by standard OpenAI clients):
    use_context: bool = True
    doc_ids: list[str] | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "model": "hexrag",
                    "messages": [{"role": "user", "content": "What is in the docs?"}],
                    "use_context": True,
                    "stream": False,
                }
            ]
        }
    }


@chat_router.post("/chat/completions", response_model=None)
def chat_completions(
    request: Request, body: ChatCompletionRequest
) -> ChatCompletion | StreamingResponse:
    service = request.state.injector.get(ChatService)
    messages = [
        ChatMessage(role=MessageRole(m.get("role", "user")), content=m.get("content", ""))
        for m in body.messages
    ]

    if body.stream:
        gen = service.stream_chat(messages, use_context=body.use_context, doc_ids=body.doc_ids)
        return StreamingResponse(to_sse_stream(gen.response), media_type="text/event-stream")

    completion = service.chat(messages, use_context=body.use_context, doc_ids=body.doc_ids)
    return completion_from_text(completion.response, sources=completion.sources)
