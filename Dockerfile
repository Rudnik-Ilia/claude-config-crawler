FROM python:3.11-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates gh && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock README.md main.py ./
COPY src ./src
RUN uv sync --locked --no-dev --no-editable

ENTRYPOINT ["/app/.venv/bin/claude-scan"]
CMD ["--help"]
