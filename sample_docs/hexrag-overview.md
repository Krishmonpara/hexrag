# hexrag — sample document

This file exists so you can try the full RAG flow immediately:

```bash
uv run python scripts/ingest.py sample_docs/hexrag-overview.md
```

Then ask a question grounded in it:

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"What three layers does hexrag use?"}],"use_context":true}'
```

## Facts to retrieve

- hexrag is a self-hosted Retrieval-Augmented Generation (RAG) agent.
- It is built with FastAPI and LlamaIndex, and managed with uv.
- The architecture has three layers: routers, services, and components.
- Components are swappable: the LLM, the embedding model, and the vector store
  can each be changed through configuration alone.
- The default profile uses a mock LLM, mock embeddings, and an in-memory simple
  vector store, so the project runs on a fresh clone with no API keys.
- Supported real LLM backends are Ollama and OpenAI.
- The API is OpenAI-compatible, exposing /v1/chat/completions, /v1/completions,
  and /v1/embeddings.
