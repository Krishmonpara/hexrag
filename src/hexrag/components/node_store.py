"""Node store component: the doc store (chunk text + parent-doc refs) and index
store. Persisted to disk so ingested data survives restarts. Kept separate from
the vector store because vectors and node metadata can live in different backends."""

from __future__ import annotations

import logging

from injector import inject, singleton
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore

from hexrag.paths import local_data_path

logger = logging.getLogger(__name__)


@singleton
class NodeStoreComponent:
    doc_store: SimpleDocumentStore
    index_store: SimpleIndexStore

    @inject
    def __init__(self) -> None:
        persist_dir = str(local_data_path)
        try:
            self.doc_store = SimpleDocumentStore.from_persist_dir(persist_dir)
        except FileNotFoundError:
            self.doc_store = SimpleDocumentStore()
        try:
            self.index_store = SimpleIndexStore.from_persist_dir(persist_dir)
        except FileNotFoundError:
            self.index_store = SimpleIndexStore()
