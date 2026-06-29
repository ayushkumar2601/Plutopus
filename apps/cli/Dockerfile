FROM python:3.12-slim

WORKDIR /app

COPY packages/schemas /app/packages/schemas
COPY apps/cli /app/apps/cli

RUN pip install --no-cache-dir -e /app/packages/schemas
RUN pip install --no-cache-dir -e /app/apps/cli

ENV PYTHONPATH=/app/apps/cli/src

ENTRYPOINT ["plutopus"]
