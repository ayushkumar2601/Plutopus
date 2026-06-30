FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY packages/schemas /app/packages/schemas
COPY packages/shared /app/packages/shared
COPY services/topology /app/services/topology
COPY services/prediction /app/services/prediction

RUN pip install --no-cache-dir -e /app/packages/schemas
RUN pip install --no-cache-dir -e /app/packages/shared
RUN pip install --no-cache-dir -e /app/services/prediction

ENV PYTHONPATH=/app/services/prediction/src:/app/services/prediction

CMD ["python", "/app/services/prediction/src/worker.py"]
