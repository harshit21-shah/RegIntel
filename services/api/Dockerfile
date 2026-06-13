# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

WORKDIR /app
RUN pip install --no-cache-dir hatchling
COPY pyproject.toml README.md ./
COPY services ./services
RUN pip wheel --no-cache-dir --wheel-dir /wheels -e .

FROM python:3.12-slim AS runtime

RUN groupadd --gid 1000 regintel && \
    useradd --uid 1000 --gid regintel --shell /bin/bash regintel && \
    apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

COPY services ./services
COPY scripts ./scripts

USER regintel
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
