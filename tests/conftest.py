"""Test fixtures. Forces the offline `test` profile and isolates data per run."""

from __future__ import annotations

import os
import tempfile

# Must be set before hexrag.settings is imported anywhere.
os.environ["HEXRAG_PROFILES"] = "test"
os.environ.setdefault("HEXRAG_DATA_FOLDER", tempfile.mkdtemp(prefix="hexrag-test-"))

import pytest  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

from hexrag.di import create_injector  # noqa: E402
from hexrag.launcher import create_app  # noqa: E402


@pytest.fixture
def injector():
    return create_injector()


@pytest.fixture
def client(injector):
    return TestClient(create_app(injector))
