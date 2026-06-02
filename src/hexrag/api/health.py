from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

health_router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


@health_router.get("/health", tags=["Health"])
def health() -> HealthResponse:
    """Liveness check — returns ok if the app booted."""
    return HealthResponse()
