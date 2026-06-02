"""Filesystem locations for persisted data (vector store, doc store)."""

from __future__ import annotations

import os
from pathlib import Path

from hexrag.settings.loader import PROJECT_ROOT

local_data_path: Path = Path(
    os.environ.get("HEXRAG_DATA_FOLDER", PROJECT_ROOT / "local_data")
)
local_data_path.mkdir(parents=True, exist_ok=True)
