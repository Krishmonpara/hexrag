<div align="center">

# 🧩 hexrag

**A clean, self-hosted RAG agent with an OpenAI-compatible API.**

Ingest your documents, then chat with answers grounded in their content — using
local models (Ollama), OpenAI, or a zero-setup mock backend.

[![CI](https://github.com/Krishmonpara/hexrag/actions/workflows/ci.yml/badge.svg)](https://github.com/Krishmonpara/hexrag/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-261230.svg)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/badge/managed%20with-uv-de5fe9.svg)](https://github.com/astral-sh/uv)

</div>

---

hexrag is built on **FastAPI + LlamaIndex** with a strict three-layer architecture
wired by dependency injection, so the **LLM, embedding model, and vector store are
all swappable via configuration alone** — no code changes.

```
HTTP (OpenAI client / curl)
   → routers   (api/)        OpenAI-compatible HTTP surface
   → services  (services/)   orchestration: ingest, retrieve, prompt, complete
   → components (components/) swappable adapters: LLM · embeddings · vector store
   ↑ Settings (profiles: settings.yaml + settings-<profile>.yaml)
```

## ✨ Highlights

- **Runs on a fresh clone with zero setup** — the default profile uses a mock LLM,
  mock embeddings, and an in-memory vector store. No API keys, no model downloads.
- **OpenAI-compatible** — `/v1/chat/completions` (with SSE streaming),
  `/v1/completions`, `/v1/embeddings`. Point any OpenAI SDK at it.
- **Swap any component with one config line** — `llm.mode`, `embedding.mode`,
  `vectorstore.database`. Ollama, OpenAI, HuggingFace, and Chroma wired in.
- **Grounded answers with sources** — every RAG response returns the retrieved
  chunks (score, text, document id) that informed it.
- **Clean, documented, tested** — DI-decoupled layers, contract + end-to-end +
  API-shape tests, ruff, CI, and Docker.

## 🚀 Quickstart

Requires [uv](https://docs.astral.sh/uv/) (it will fetch Python 3.12 for you).

```bash
git clone https://github.com/Krishmonpara/hexrag.git
cd hexrag
uv sync          # install
uv run hexrag    # serve http://localhost:8001  (mock backend, no setup)
```

Or with Make / Docker:

```bash
make run                      # same as uv run hexrag
docker compose up --build     # containerized
```

Health check:

```bash
curl http://localhost:8001/health
# {"status":"ok"}
```

### Try the full RAG flow

```bash
# 1. ingest the bundled sample document
uv run python scripts/ingest.py sample_docs/hexrag-overview.md

# 2. ask a grounded question (OpenAI-compatible payload)
curl -X POST http://localhost:8001/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
        "model": "hexrag",
        "messages": [{"role":"user","content":"What three layers does hexrag use?"}],
        "use_context": true
      }'
```

The response includes a `choices[].sources` array with the retrieved chunks.
Interactive API docs: <http://localhost:8001/docs>

> [!NOTE]
> The default profile uses a **mock LLM**, so the *answer text* is a placeholder
> (it echoes the assembled grounded prompt). Retrieval, grounding, sources, and
> the full API shape are real. Switch to a real backend below for real answers.

## 🔌 Switching backends (the whole point of the design)

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

| Concern       | Setting                | Options                                   | Install                 |
|---------------|------------------------|-------------------------------------------|-------------------------|
| LLM           | `llm.mode`             | `mock`, `ollama`, `openai`                | `--extra ollama/openai` |
| Embeddings    | `embedding.mode`       | `mock`, `ollama`, `openai`, `huggingface` | matching extra          |
| Vector store  | `vectorstore.database` | `simple`, `chroma`                        | `--extra chroma`        |

## 🧠 How it works

**Ingestion** — a file is read, split into chunks (`SentenceSplitter`), each chunk
is stamped with its parent `doc_id`, embedded, and persisted to the vector store +
doc store.

**Query** — the incoming messages are split into system / history / last question;
the question is embedded and used to retrieve the top-k chunks (optionally filtered
by `doc_ids`); a `ContextChatEngine` assembles a grounded prompt and calls the LLM;
the answer is returned with its source chunks.

```
HTTP client (OpenAI SDK / curl)
        │  POST /v1/chat/completions
        ▼
   api/chat.py            ── routers: HTTP ↔ domain, OpenAI schema
        │ injector.get(ChatService)
        ▼
   services/chat.py       ── retriever + chat engine orchestration
     │        │        │
     ▼        ▼        ▼
  vector   embedding   llm        ── components: swappable adapters
  store    model       (mock/ollama/openai)
        ▲
        │ reads
   Settings (YAML profiles selected by HEXRAG_PROFILES)
```

Dependency injection (`injector`) supplies each layer with the one beneath it, so
`ChatService` depends on an `LLM` interface and never knows which backend is behind
it. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a new backend.

## 📂 Project layout

```
src/hexrag/
  main.py · launcher.py · di.py · paths.py
  settings/   loader.py (profile merge + ${ENV})   models.py (typed tree)
  components/ llm.py  embedding.py  vector_store.py  node_store.py
  services/   ingest.py  chat.py  index.py
  api/        chat.py  completions.py  embeddings.py  ingest.py  health.py  openai_schema.py
  ui/         app.py    (optional Gradio chat UI)
tests/        contract · end-to-end · API-shape
scripts/      ingest.py (CLI)
settings*.yaml  default + mock/ollama/openai/test profiles
```

## 🛠️ Development

```bash
make help      # list all commands
make check     # lint + tests
make format    # ruff fix + format
make wipe      # delete ingested data
```

Tests run fully offline against the mock profile.

## 📡 API reference

| Method & path             | Description                                  |
|---------------------------|----------------------------------------------|
| `GET /health`             | Liveness check                               |
| `POST /v1/chat/completions` | Chat, OpenAI-compatible (RAG via `use_context`) |
| `POST /v1/completions`    | Legacy text completion (delegates to chat)   |
| `POST /v1/embeddings`     | Embed text, OpenAI-compatible                |
| `POST /ingest/text`       | Ingest raw text                              |
| `POST /ingest/file`       | Ingest an uploaded file                      |
| `GET /ingest/list`        | List ingested documents                      |

Full interactive schema at `/docs` when the server is running.

## Troubleshooting

**`ModuleNotFoundError: No module named 'hexrag'` when the path contains spaces.**
`uv`'s editable install uses a bare-path `.pth` file, which Python's startup may
skip if the project's absolute path contains spaces (e.g. `My Projects/`). Either
clone into a space-free path, or install non-editable:

```bash
UV_NO_EDITABLE=1 uv sync
UV_NO_EDITABLE=1 uv run hexrag
```

**Run from the project root.** Settings are loaded from the current working
directory by default; run commands from the repo root, or set
`HEXRAG_SETTINGS_FOLDER=/path/to/settings`.

## License

[Apache-2.0](LICENSE). This project began as a study of the architecture of
[PrivateGPT](https://github.com/zylon-ai/private-gpt) and was reimplemented from
scratch in its own structure.
