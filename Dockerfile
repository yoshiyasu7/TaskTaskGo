# ========================================================
# Stage 1: Builder — install dependencies in isolated venv
# ========================================================
FROM python:3.13-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true && \
    poetry install --only main --no-root --no-interaction --no-ansi

# ========================================================
# Stage 2: Runtime — minimal production image
# ========================================================
FROM python:3.13-slim AS runtime

LABEL org.opencontainers.image.title="TaskTaskGo" \
      org.opencontainers.image.description="Task Management API" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="Maxim Shadrin <max.wojw@gmail.com>"

RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/sh --create-home appuser

WORKDIR /app

COPY --from=builder /build/.venv ./.venv

COPY src/ ./src/
COPY static/ ./static/
COPY templates/ ./templates/
COPY settings/settings.json ./settings/settings.json

RUN mkdir -p logs && chown -R appuser:appuser /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request as u; p=os.getenv('HOST_PORT','8000'); u.urlopen(f'http://localhost:{p}/docs')"]

CMD ["python", "-m", "src.main"]
