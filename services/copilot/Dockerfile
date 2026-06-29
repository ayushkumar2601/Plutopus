FROM python:3.12-slim

WORKDIR /app

COPY packages/shared /app/packages/shared
COPY services/copilot /app/services/copilot

RUN pip install --no-cache-dir -e /app/packages/shared
RUN pip install --no-cache-dir -e /app/services/copilot

CMD ["python", "-c", "import time; import logging; logging.basicConfig(level=logging.INFO); logger = logging.getLogger('copilot-worker'); logger.info('Plutopus Copilot Worker Service initialized.'); [time.sleep(3600) for _ in iter(int, 1)]"]
