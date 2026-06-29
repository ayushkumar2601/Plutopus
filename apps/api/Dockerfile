FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy packages and application
COPY packages/schemas /app/packages/schemas
COPY apps/api /app/apps/api

# Install shared schemas package and backend API package
RUN pip install --no-cache-dir -e /app/packages/schemas
RUN pip install --no-cache-dir -e /app/apps/api

EXPOSE 8000

ENV PYTHONPATH=/app/apps/api/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app/apps/api/src"]
