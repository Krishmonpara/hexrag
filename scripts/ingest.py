"""CLI: ingest one or more files into the active profile's stores.

Usage: uv run python scripts/ingest.py FILE [FILE ...]
"""

from __future__ import annotations

import sys
from pathlib import Path

from hexrag.di import global_injector
from hexrag.services.ingest import IngestService


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    service = global_injector.get(IngestService)
    for arg in argv:
        path = Path(arg)
        if not path.exists():
            print(f"skip (not found): {path}")
            continue
        docs = service.ingest_file(path.name, path)
        print(f"ingested {path.name} -> {len(docs)} document(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
