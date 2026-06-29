FROM python:3.12-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY packages/schemas /app/packages/schemas
COPY packages/shared /app/packages/shared
COPY services/telemetry /app/services/telemetry

RUN pip install --no-cache-dir -e /app/packages/schemas
RUN pip install --no-cache-dir -e /app/packages/shared
RUN pip install --no-cache-dir -e /app/services/telemetry

ENV PYTHONPATH=/app/services/telemetry/src

CMD ["python", "/app/services/telemetry/src/main.py"]
