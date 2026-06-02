"""End-to-end RAG: ingest a document, then confirm a query retrieves it as a
grounded source."""

from llama_index.core.llms import ChatMessage, MessageRole

from hexrag.services.chat import ChatService
from hexrag.services.ingest import IngestService


def test_ingest_then_retrieve_returns_sources(injector):
    ingest = injector.get(IngestService)
    docs = ingest.ingest_text(
        "sales.txt", "Outbound sales increased 20% in Q2, driven by new leads."
    )
    assert len(docs) == 1
    assert docs[0].doc_id

    assert any(d.doc_id == docs[0].doc_id for d in ingest.list_ingested())

    chat = injector.get(ChatService)
    completion = chat.chat(
        [ChatMessage(role=MessageRole.USER, content="How did outbound sales do?")],
        use_context=True,
    )
    assert completion.sources, "expected at least one retrieved source"
    assert "Outbound sales" in completion.sources[0].text
    assert completion.sources[0].doc_id == docs[0].doc_id


def test_ingested_data_persists_across_a_new_injector(injector):
    """Data ingested in one process is reloaded from disk by a fresh container."""
    from hexrag.di import create_injector

    ingest = injector.get(IngestService)
    docs = ingest.ingest_text("persist.txt", "The capital of Atlantis is Marigold City.")

    # Simulate a restart: brand-new injector -> components reload from disk.
    fresh = create_injector()
    assert any(d.doc_id == docs[0].doc_id for d in fresh.get(IngestService).list_ingested())
    completion = fresh.get(ChatService).chat(
        [ChatMessage(role=MessageRole.USER, content="What is the capital of Atlantis?")],
        use_context=True,
    )
    assert any("Marigold City" in s.text for s in completion.sources)


def test_chat_without_context_returns_no_sources(injector):
    chat = injector.get(ChatService)
    completion = chat.chat(
        [ChatMessage(role=MessageRole.USER, content="hello")], use_context=False
    )
    assert completion.sources == []
