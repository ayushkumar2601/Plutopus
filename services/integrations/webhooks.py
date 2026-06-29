import urllib.request
import urllib.error
import json
import time
import logging
from typing import Dict, Any

logger = logging.getLogger("webhook-integrations")

class WebhookIntegrationService:
    @staticmethod
    def dispatch_webhook(url: str, payload: Dict[str, Any], retries: int = 3, backoff: float = 1.0) -> bool:
        """
        Dispatches an incident payload to an external NOC webhook endpoint.
        Retries on connection errors using exponential backoff.
        """
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        for attempt in range(1, retries + 1):
            try:
                # 3-second timeout constraint
                with urllib.request.urlopen(req, timeout=3.0) as response:
                    if response.status in (200, 201, 202):
                        logger.info(f"Webhook delivered successfully to {url} on attempt {attempt}")
                        return True
                    else:
                        logger.warning(f"Webhook received status {response.status} from {url}")
            except Exception as e:
                logger.warning(f"Attempt {attempt} failed to deliver webhook to {url}: {e}")
                if attempt < retries:
                    time.sleep(backoff * (2 ** (attempt - 1)))

        logger.error(f"Failed to deliver webhook to {url} after {retries} attempts.")
        return False
