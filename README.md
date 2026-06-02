# hexrag

A clean, self-hosted **RAG agent** with an **OpenAI-compatible API**, built on
FastAPI + LlamaIndex. Ingest documents, then chat with answers grounded in their
content — using local models (Ollama), OpenAI, or a zero-setup mock backend.

The architecture is a strict three-layer onion wired with dependency injection,
so the LLM, embedding model, and vector store are all swappable via config alone.

```
HTTP (OpenAI client / curl)
   → routers  (api/)        OpenAI-compatible HTTP surface
   → services (services/)   orchestration: ingest, retrieve, prompt, complete
   → components (components/) swappable adapters: LLM · embeddings · vector store
   ↑ Settings (profiles: settings.yaml + settings-<profile>.yaml)
```

## Why it's interesting

- **Runs on a fresh clone with no API keys or model downloads** — the default
  profile uses a mock LLM + mock embeddings + in-memory vector store.
- **OpenAI-compatible** `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`
  — point any OpenAI SDK at it.
- **Swap any component with one config line** — `llm.mode`, `embedding.mode`,
  `vectorstore.database`. Real backends (Ollama, OpenAI, HuggingFace, Chroma) wired in.
- **Dependency injection** decouples HTTP from orchestration from infrastructure.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11+ (`uv` will fetch it).

```bash
uv sync                 # install core deps
uv run hexrag           # serve on http://localhost:8001  (mock backend, no setup)
```

Health check:

```bash
curl http://localhost:8001/health
# {"status":"ok"}
```

Ingest a document, then ask about it:

```bash
# 1. ingest some text
curl -X POST http://localhost:8001/ingest/text \
  -H 'Content-Type: application/json' \
  -d '{"file_name":"notes.txt","text":"Project Hex shipped v2 on June 1st 2026."}'

# 2. chat with retrieval (OpenAI-compatible payload)
curl -X POST http://localhost:8001/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
        "model": "hexrag",
        "messages": [{"role":"user","content":"When did Hex ship v2?"}],
        "use_context": true
      }'
```

Interactive API docs: <http://localhost:8001/docs>

> The default profile uses a **mock LLM**, so the *answer text* is placeholder —
> but retrieval, grounding, sources, and the full API shape are real. Switch to a
> real backend below to get real answers.

## Switching backends (the whole point of the design)

Select a profile with `HEXRAG_PROFILES`; it deep-merges `settings-<profile>.yaml`
over `settings.yaml`. No code changes.

### Local & private — Ollama

```bash
# install Ollama from https://ollama.com, then:
ollama pull llama3.2
ollama pull nomic-embed-text

uv sync --extra ollama
HEXRAG_PROFILES=ollama uv run hexrag
```

### OpenAI

```bash
uv sync --extra openai
HEXRAG_PROFILES=openai OPENAI_API_KEY=sk-... uv run hexrag
```

### Swappable components at a glance

| Concern       | Setting               | Options                                   | Extra to install        |
|---------------|-----------------------|-------------------------------------------|-------------------------|
| LLM           | `llm.mode`            | `mock`, `ollama`, `openai`                | `--extra ollama/openai` |
| Embeddings    | `embedding.mode`      | `mock`, `ollama`, `openai`, `huggingface` | matching extra          |
| Vector store  | `vectorstore.database`| `simple`, `chroma`                        | `--extra chroma`        |

Stack profiles too: `HEXRAG_PROFILES=ollama,chroma` (if you add a chroma profile).

## CLI ingestion

```bash
uv run python scripts/ingest.py path/to/file.pdf
```

## Project layout

```
src/hexrag/
  main.py · launcher.py · di.py · paths.py
  settings/   loader.py (profile merge + ${ENV})  models.py (typed tree)
  components/ llm.py  embedding.py  vector_store.py  node_store.py
  services/   ingest.py  chat.py
  api/        chat.py  completions.py  embeddings.py  ingest.py  health.py  openai_schema.py
  ui/         app.py   (optional Gradio chat UI)
tests/        contract + end-to-end + API-shape tests
```

## Development

```bash
uv run pytest      # tests (offline, mock profile)
uv run ruff check  # lint
```

## License

Apache-2.0.
