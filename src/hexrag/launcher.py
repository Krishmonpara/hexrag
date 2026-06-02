"""Build the FastAPI app: bind the injector to each request, mount routers,
configure CORS, and optionally mount the UI."""

from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from injector import Injector

from hexrag.api.chat import chat_router
from hexrag.api.completions import completions_router
from hexrag.api.embeddings import embeddings_router
from hexrag.api.health import health_router
from hexrag.api.ingest import ingest_router
from hexrag.settings.models import Settings

logger = logging.getLogger(__name__)


def create_app(root_injector: Injector) -> FastAPI:
    async def bind_injector_to_request(request: Request) -> None:
        request.state.injector = root_injector

    app = FastAPI(
        title="hexrag",
        version="0.1.0",
        description="Self-hosted RAG agent with an OpenAI-compatible API.",
        dependencies=[Depends(bind_injector_to_request)],
    )

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(completions_router)
    app.include_router(embeddings_router)
    app.include_router(ingest_router)

    settings = root_injector.get(Settings)
    if settings.cors.enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors.allow_origins,
            allow_methods=settings.cors.allow_methods,
            allow_headers=settings.cors.allow_headers,
        )

    if settings.ui.enabled:
        try:
            from hexrag.ui.app import HexRagUI
        except ImportError as e:
            raise ImportError("UI deps not installed. Run: uv sync --extra ui") from e
        HexRagUI(root_injector).mount_in_app(app, settings.ui.path)

    return app
