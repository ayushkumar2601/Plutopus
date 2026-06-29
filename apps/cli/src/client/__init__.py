import os
import requests
from typing import Dict, Any

class PlutopusClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("PLUTOPUS_API_URL", "http://localhost:8000")

    def check_health(self) -> Dict[str, Any]:
        """
        Queries /health endpoint of Plutopus API.
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
