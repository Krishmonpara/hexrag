"""Vector store component: builds one `BasePydanticVectorStore` and knows how to
produce a retriever with an optional doc-id filter.

`simple` (in-memory + JSON persist) runs with zero external services — the
default so the project works on a fresh clone. `chroma` is the opt-in real store
that proves the abstraction swaps cleanly."""

from __future__ import annotations

import logging

from injector import inject, singleton
from llama_index.core.indices.vector_store import VectorIndexRetriever, VectorStoreIndex
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.vector_stores.types import (
    BasePydanticVectorStore,
    FilterCondition,
    MetadataFilter,
    MetadataFilters,
)

from hexrag.paths import local_data_path
from hexrag.settings.models import Settings

logger = logging.getLogger(__name__)


def _doc_id_filter(doc_ids: list[str] | None) -> MetadataFilters | None:
    if not doc_ids:
        return None
    return MetadataFilters(
        filters=[MetadataFilter(key="doc_id", value=d) for d in doc_ids],
        condition=FilterCondition.OR,
    )


@singleton
class VectorStoreComponent:
    vector_store: BasePydanticVectorStore

    @inject
    def __init__(self, settings: Settings) -> None:
        database = settings.vectorstore.database
        logger.info("Initializing vector store database=%s", database)
        match database:
            case "simple":
                # StorageContext.persist() writes embeddings to
                # "default__vector_store.json" in the data dir. Reload from there
                # if present so ingested data survives restarts; else start empty.
                from llama_index.core.storage.storage_context import VECTOR_STORE_FNAME
                from llama_index.core.vector_stores.simple import (
                    DEFAULT_VECTOR_STORE,
                    NAMESPACE_SEP,
                )

                fname = f"{DEFAULT_VECTOR_STORE}{NAMESPACE_SEP}{VECTOR_STORE_FNAME}"
                persist_path = local_data_path / fname
                if persist_path.exists():
                    self.vector_store = SimpleVectorStore.from_persist_path(str(persist_path))
                else:
                    self.vector_store = SimpleVectorStore()
            case "chroma":
                try:
                    import chromadb
                    from llama_index.vector_stores.chroma import ChromaVectorStore
                except ImportError as e:
                    raise ImportError(
                        "Chroma deps not installed. Run: uv sync --extra chroma"
                    ) from e
                client = chromadb.PersistentClient(path=str(local_data_path / "chroma_db"))
                collection = client.get_or_create_collection("hexrag")
                self.vector_store = ChromaVectorStore(chroma_collection=collection)
            case _:
                raise ValueError(f"Unsupported vectorstore.database: {database}")

    def get_retriever(
        self,
        index: VectorStoreIndex,
        similarity_top_k: int = 3,
        doc_ids: list[str] | None = None,
    ) -> VectorIndexRetriever:
        return VectorIndexRetriever(
            index=index,
            similarity_top_k=similarity_top_k,
            filters=_doc_id_filter(doc_ids),
        )
