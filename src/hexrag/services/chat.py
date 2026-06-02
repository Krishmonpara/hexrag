"""Chat orchestration: retrieve top-k chunks, assemble a grounded prompt, call
the LLM, and return the answer with its source chunks.

`use_context=True` builds a ContextChatEngine over the retriever (RAG);
`use_context=False` is a plain chat with no retrieval."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from injector import inject, singleton
from llama_index.core.chat_engine import ContextChatEngine, SimpleChatEngine
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.storage import StorageContext
from pydantic import BaseModel

from hexrag.components.embedding import EmbeddingComponent
from hexrag.components.llm import LLMComponent
from hexrag.components.node_store import NodeStoreComponent
from hexrag.components.vector_store import VectorStoreComponent
from hexrag.services.index import build_index
from hexrag.settings.models import Settings


class Source(BaseModel):
    """A retrieved chunk that grounded the answer."""

    score: float
    text: str
    doc_id: str
    file_name: str | None = None


class Completion(BaseModel):
    response: str
    sources: list[Source] = []


@dataclass
class CompletionGen:
    response: Iterator[str]
    sources: list[Source]


@singleton
class ChatService:
    @inject
    def __init__(
        self,
        settings: Settings,
        llm_component: LLMComponent,
        vector_store_component: VectorStoreComponent,
        embedding_component: EmbeddingComponent,
        node_store_component: NodeStoreComponent,
    ) -> None:
        self.settings = settings
        self.llm = llm_component.llm
        self.vector_store_component = vector_store_component
        self.storage_context = StorageContext.from_defaults(
            vector_store=vector_store_component.vector_store,
            docstore=node_store_component.doc_store,
            index_store=node_store_component.index_store,
        )
        self.index = build_index(self.storage_context, embedding_component.embedding_model)

    def _chat_engine(
        self, system_prompt: str, use_context: bool, doc_ids: list[str] | None
    ) -> BaseChatEngine:
        if not use_context:
            return SimpleChatEngine.from_defaults(llm=self.llm, system_prompt=system_prompt)
        retriever = self.vector_store_component.get_retriever(
            index=self.index,
            similarity_top_k=self.settings.rag.similarity_top_k,
            doc_ids=doc_ids,
        )
        return ContextChatEngine.from_defaults(
            retriever=retriever, llm=self.llm, system_prompt=system_prompt
        )

    def _split(self, messages: list[ChatMessage]) -> tuple[str, str, list[ChatMessage]]:
        """Return (system_prompt, last_user_message, prior_history)."""
        system_prompt = self.settings.llm.system_prompt
        msgs = list(messages)
        if msgs and msgs[0].role == MessageRole.SYSTEM:
            system_prompt = msgs.pop(0).content or system_prompt
        last_message = ""
        if msgs and msgs[-1].role == MessageRole.USER:
            last_message = msgs.pop(-1).content or ""
        return system_prompt, last_message, msgs

    @staticmethod
    def _sources(source_nodes) -> list[Source]:
        return [
            Source(
                score=n.score or 0.0,
                text=n.node.get_content(),
                doc_id=n.node.metadata.get("doc_id", n.node.ref_doc_id or "-"),
                file_name=n.node.metadata.get("file_name"),
            )
            for n in source_nodes
        ]

    def chat(
        self,
        messages: list[ChatMessage],
        use_context: bool = False,
        doc_ids: list[str] | None = None,
    ) -> Completion:
        system_prompt, last_message, history = self._split(messages)
        engine = self._chat_engine(system_prompt, use_context, doc_ids)
        result = engine.chat(message=last_message, chat_history=history)
        return Completion(response=str(result.response), sources=self._sources(result.source_nodes))

    def stream_chat(
        self,
        messages: list[ChatMessage],
        use_context: bool = False,
        doc_ids: list[str] | None = None,
    ) -> CompletionGen:
        system_prompt, last_message, history = self._split(messages)
        engine = self._chat_engine(system_prompt, use_context, doc_ids)
        result = engine.stream_chat(message=last_message, chat_history=history)
        return CompletionGen(
            response=result.response_gen, sources=self._sources(result.source_nodes)
        )
