import os
import json
import urllib.request
import urllib.error
import logging
from typing import Dict, Any, List

logger = logging.getLogger("copilot-llm")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen:0.5b")

def call_ollama(prompt: str, system_prompt: str = "") -> str:
    """
    Sends a generation request to the local Ollama daemon.
    Includes timeouts and handles failures gracefully using deterministic fallbacks.
    """
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 256
        }
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    # 4 second timeout constraint
    try:
        with urllib.request.urlopen(req, timeout=4.0) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("response", "").strip()
    except Exception as e:
        logger.warning(f"Ollama call failed or timed out: {e}. Executing fallback response pipeline.")
        return ""

def generate_fallback_response(
    query: str, 
    context: Dict[str, Any], 
    runbook_contents: str
) -> str:
    """
    Formulates a structured diagnostic response deterministically when the LLM is unavailable.
    """
    lines = [
        "### Antigravity NOC Assistant (Fallback Grounded Mode)",
        "",
        "The offline predictive analytics engine suggests the following diagnostic summary:",
        ""
    ]
    
    # Render Site context summary if present
    if "site_id" in context:
        lines.append(f"**Entity**: Site `{context['site_id']}` ({context['name']})")
        lines.append(f"- **Risk Level**: {context['risk_score']} ({context['risk_level'].upper()})")
        if context.get("signals"):
            lines.append("- **Signals Contributing to Risk**:")
            for sig in context["signals"]:
                lines.append(f"  * {sig.get('metric', 'Metric')} (Impact Weight: {sig.get('impact')})")
        if context.get("active_anomalies"):
            lines.append("- **Active Telemetry Anomaly Detections**:")
            for a in context["active_anomalies"]:
                lines.append(f"  * {a.get('description')}")
                
    # Render Tunnel context summary if present
    elif "tunnel_id" in context:
        lines.append(f"**Entity**: SD-WAN Tunnel `{context['tunnel_id']}`")
        lines.append(f"- **Current State**: {context['status'].upper()}")
        lines.append(f"- **Risk Score**: {context['risk_score']} ({context['risk_level'].upper()})")
        metrics = context.get("metrics", {})
        lines.append(f"- **Latency**: {metrics.get('latency')}ms | **Packet Loss**: {metrics.get('packet_loss')}%")

    if runbook_contents:
        lines.append("")
        lines.append("### Recommended Runbook Procedures:")
        lines.append(runbook_contents)

    lines.append("")
    lines.append("---")
    lines.append("### Sources:")
    lines.append("- Database Site State Indices")
    if "site_id" in context:
        lines.append(f"- Site Risk Assessment (`{context['site_id']}`)")
    elif "tunnel_id" in context:
        lines.append(f"- Tunnel Metrics (`{context['tunnel_id']}`)")
    if runbook_contents:
        lines.append("- Matching Troubleshooting Markdown Runbooks")
        
    return "\n".join(lines)
