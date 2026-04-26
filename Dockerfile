FROM astral/uv:0.9.2-python3.14-alpine AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

FROM astral/uv:0.9.2-python3.14-alpine

RUN apk add --no-cache make \
    postgresql-client

RUN addgroup -g 1000 appgroup && \
    adduser -D -u 1000 -G appgroup appuser

WORKDIR /app
RUN chown appuser:appgroup /app

COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

COPY --chown=appuser:appgroup . /app
RUN if [ -f /app/.env ]; then sed -i 's/\r$//' /app/.env; fi
RUN chmod +x scripts/run.sh

USER appuser

CMD ["./scripts/run.sh"]