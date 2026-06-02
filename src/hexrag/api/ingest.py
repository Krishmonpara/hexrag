"""Ingestion endpoints (hexrag-specific, not part of the OpenAI surface)."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Request, UploadFile
from pydantic import BaseModel

from hexrag.services.ingest import IngestedDoc, IngestService

ingest_router = APIRouter(prefix="/ingest", tags=["Ingestion"])


class IngestResponse(BaseModel):
    object: str = "list"
    data: list[IngestedDoc]


class IngestTextRequest(BaseModel):
    file_name: str
    text: str


@ingest_router.post("/file")
async def ingest_file(request: Request, file: UploadFile) -> IngestResponse:
    service = request.state.injector.get(IngestService)
    contents = await file.read()
    suffix = Path(file.filename or "upload.txt").suffix or ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(contents)
        tmp_path = Path(tmp.name)
    try:
        docs = service.ingest_file(file.filename or tmp_path.name, tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
    return IngestResponse(data=docs)


@ingest_router.post("/text")
def ingest_text(request: Request, body: IngestTextRequest) -> IngestResponse:
    service = request.state.injector.get(IngestService)
    return IngestResponse(data=service.ingest_text(body.file_name, body.text))


@ingest_router.get("/list")
def list_ingested(request: Request) -> IngestResponse:
    service = request.state.injector.get(IngestService)
    return IngestResponse(data=service.list_ingested())
