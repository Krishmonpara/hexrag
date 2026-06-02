# hexrag container image. Uses the official uv base image for fast, reproducible
# installs. Builds the mock profile by default; override HEXRAG_PROFILES at runtime.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    HEXRAG_HOST=0.0.0.0 \
    HEXRAG_PORT=8001

WORKDIR /app

# Install dependencies first (cached layer) using only the lock + metadata.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev

# Now copy the source and install the project itself.
COPY src ./src
COPY settings*.yaml ./
COPY scripts ./scripts
RUN uv sync --frozen --no-dev

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8001/health').status==200 else 1)"

CMD ["uv", "run", "--no-dev", "hexrag"]
