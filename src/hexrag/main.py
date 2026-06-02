"""ASGI entrypoint: `uvicorn hexrag.main:app`."""

from hexrag.di import global_injector
from hexrag.launcher import create_app

app = create_app(global_injector)
