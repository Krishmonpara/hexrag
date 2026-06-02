"""Shared helper to build/load the VectorStoreIndex from a storage context.

Works uniformly for stores that persist text in an index store (e.g. the default
SimpleVectorStore) and stores that hold text themselves (e.g. Chroma): on boot we
try to load the persisted index, and otherwise create a fresh empty one."""

from __future__ import annotations

from llama_index.core import VectorStoreIndex, load_index_from_storage
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.storage import StorageContext


def build_index(storage_context: StorageContext, embed_model: BaseEmbedding) -> VectorStoreIndex:
    try:
        index = load_index_from_storage(storage_context, embed_model=embed_model)
        assert isinstance(index, VectorStoreIndex)
        return index
    except ValueError:
        # No index persisted yet — start empty.
        return VectorStoreIndex(
            nodes=[], storage_context=storage_context, embed_model=embed_model
        )
