"""`hexrag` / `python -m hexrag` — run the dev server with uvicorn."""

from __future__ import annotations

import uvicorn

from hexrag.settings.models import unsafe_typed_settings as settings


def main() -> None:
    uvicorn.run(
        "hexrag.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
