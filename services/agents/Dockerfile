# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

WORKDIR /app
RUN pip install --no-cache-dir hatchling
COPY pyproject.toml README.md ./
COPY services ./services
RUN pip wheel --no-cache-dir --wheel-dir /wheels -e ".[ml]"

FROM python:3.12-slim AS runtime

RUN groupadd --gid 1000 regintel && \
    useradd --uid 1000 --gid regintel --shell /bin/bash regintel

WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

COPY services ./services

USER regintel

CMD ["python", "-m", "services.agents.worker"]
