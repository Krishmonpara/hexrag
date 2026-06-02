# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows
[Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-06-01

Initial release.

### Added
- Three-layer architecture (routers → services → components) wired with
  dependency injection (`injector`).
- OpenAI-compatible API: `/v1/chat/completions` (incl. SSE streaming),
  `/v1/completions`, `/v1/embeddings`.
- Ingestion API + CLI: `/ingest/text`, `/ingest/file`, `/ingest/list`,
  `scripts/ingest.py`.
- Retrieval-augmented chat with grounded answers and returned source chunks.
- Swappable components selected by config:
  - LLM: `mock`, `ollama`, `openai`
  - Embeddings: `mock`, `ollama`, `openai`, `huggingface`
  - Vector store: `simple`, `chroma`
- YAML settings profiles merged via `HEXRAG_PROFILES`, with `${ENV:default}`
  interpolation.
- Runs fully offline on a fresh clone (mock default) — no keys or downloads.
- Optional Gradio UI (`--extra ui`).
- Test suite (component contracts, end-to-end RAG, OpenAI schema shape),
  ruff config, GitHub Actions CI, Dockerfile + docker-compose.

[0.1.0]: https://github.com/Krishmonpara/hexrag/releases/tag/v0.1.0
