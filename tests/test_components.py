"""Contract tests: each component satisfies its LlamaIndex base interface, so any
implementation is swappable behind the same type."""

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.core.vector_stores.types import BasePydanticVectorStore

from hexrag.components.embedding import EmbeddingComponent
from hexrag.components.llm import LLMComponent
from hexrag.components.vector_store import VectorStoreComponent


def test_llm_component_provides_an_llm(injector):
    component = injector.get(LLMComponent)
    assert isinstance(component.llm, LLM)


def test_embedding_component_provides_a_base_embedding(injector):
    component = injector.get(EmbeddingComponent)
    assert isinstance(component.embedding_model, BaseEmbedding)


def test_embedding_dimension_matches_settings(injector):
    component = injector.get(EmbeddingComponent)
    vector = component.embedding_model.get_text_embedding("hello world")
    assert len(vector) == 384


def test_vector_store_component_provides_a_store(injector):
    component = injector.get(VectorStoreComponent)
    assert isinstance(component.vector_store, BasePydanticVectorStore)


def test_components_are_singletons(injector):
    assert injector.get(LLMComponent) is injector.get(LLMComponent)
