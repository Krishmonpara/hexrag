# Contributing to hexrag

Thanks for your interest! hexrag is a small, deliberately readable RAG codebase —
contributions that keep it clean and well-explained are very welcome.

## Development setup

```bash
git clone https://github.com/Krishmonpara/hexrag.git
cd hexrag
uv sync                       # installs deps + dev tools (Python 3.12 via uv)
uv tool install pre-commit    # optional
pre-commit install            # optional: run hooks on commit
```

## Before opening a PR

```bash
make format   # ruff fix + format
make check    # lint + tests
```

All tests run fully offline against the mock backend — no API keys or model
downloads required.

## Architecture in 30 seconds

Three layers, dependencies point inward:

- `api/` — FastAPI routers. HTTP ↔ domain only, no business logic.
- `services/` — orchestration (`IngestService`, `ChatService`).
- `components/` — swappable adapters behind LlamaIndex interfaces
  (`LLM`, `BaseEmbedding`, `BasePydanticVectorStore`).

Wiring is via `injector` (see `di.py`). Configuration is YAML profiles merged by
`HEXRAG_PROFILES` (see `settings/loader.py`).

### Adding a new backend

1. Add a branch to the relevant component (`components/llm.py`, etc.).
2. Add the `mode`/`database` literal to `settings/models.py`.
3. Add the dependency as an optional extra in `pyproject.toml`.
4. Add a `settings-<name>.yaml` profile and document it in the README table.

Keep imports of heavy/optional dependencies *inside* the matching branch so the
core install stays light.

## Style

- Python 3.11+, type hints, `ruff` for lint + format (line length 100).
- Prefer clarity over cleverness; explain non-obvious decisions in a short comment.

## License

By contributing you agree your contributions are licensed under Apache-2.0.
