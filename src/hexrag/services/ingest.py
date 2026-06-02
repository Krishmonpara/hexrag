"""Ingestion: load a file -> chunk into nodes -> embed -> persist vectors + nodes.

Uses LlamaIndex's VectorStoreIndex as the orchestrator: given a StorageContext
(vector store + doc store + index store) and an embed model, `insert` runs the
chunk->embed->store pipeline for us. We stamp each node with its parent `doc_id`
so retrieval can be filtered per-document."""

from __future__ import annotations

import logging
from pathlib import Path

from injector import inject, singleton
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage import StorageContext
from pydantic import BaseModel

from hexrag.components.embedding import EmbeddingComponent
from hexrag.components.node_store import NodeStoreComponent
from hexrag.components.vector_store import VectorStoreComponent
from hexrag.paths import local_data_path
from hexrag.services.index import build_index

logger = logging.getLogger(__name__)


class IngestedDoc(BaseModel):
    object: str = "ingest.document"
    doc_id: str
    doc_metadata: dict | None = None


@singleton
class IngestService:
    @inject
    def __init__(
        self,
        vector_store_component: VectorStoreComponent,
        embedding_component: EmbeddingComponent,
        node_store_component: NodeStoreComponent,
    ) -> None:
        self.storage_context = StorageContext.from_defaults(
            vector_store=vector_store_component.vector_store,
            docstore=node_store_component.doc_store,
            index_store=node_store_component.index_store,
        )
        self.embed_model = embedding_component.embedding_model
        self.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=64)
        self.index = build_index(self.storage_context, self.embed_model)

    def _persist(self) -> None:
        self.storage_context.persist(persist_dir=str(local_data_path))

    def _ingest_documents(self, documents: list[Document]) -> list[IngestedDoc]:
        nodes = self.node_parser.get_nodes_from_documents(documents)
        for node in nodes:
            node.metadata["doc_id"] = node.ref_doc_id
        self.index.insert_nodes(nodes)
        self._persist()
        seen: dict[str, IngestedDoc] = {}
        for doc in documents:
            seen[doc.doc_id] = IngestedDoc(doc_id=doc.doc_id, doc_metadata=doc.metadata or None)
        logger.info("Ingested %d nodes from %d document(s)", len(nodes), len(seen))
        return list(seen.values())

    def ingest_file(self, file_name: str, file_path: Path) -> list[IngestedDoc]:
        logger.info("Ingesting file=%s", file_name)
        documents = SimpleDirectoryReader(input_files=[str(file_path)]).load_data()
        for doc in documents:
            doc.metadata["file_name"] = file_name
        return self._ingest_documents(documents)

    def ingest_text(self, file_name: str, text: str) -> list[IngestedDoc]:
        document = Document(text=text, metadata={"file_name": file_name})
        return self._ingest_documents([document])

    def list_ingested(self) -> list[IngestedDoc]:
        ref_docs = self.storage_context.docstore.get_all_ref_doc_info() or {}
        return [
            IngestedDoc(doc_id=doc_id, doc_metadata=info.metadata or None)
            for doc_id, info in ref_docs.items()
        ]
