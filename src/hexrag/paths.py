"""Filesystem locations for persisted data (vector store, doc store)."""

from __future__ import annotations

import os
from pathlib import Path

# Where ingested data (vectors, doc store) is persisted. Defaults to ./local_data
# under the current working directory; override with HEXRAG_DATA_FOLDER.
local_data_path: Path = Path(
    os.environ.get("HEXRAG_DATA_FOLDER", Path.cwd() / "local_data")
)
local_data_path.mkdir(parents=True, exist_ok=True)
