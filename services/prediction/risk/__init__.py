from typing import List, Dict, Any, Tuple

def calculate_tunnel_risk(
    tunnel_id: str,
    latency: float,
    packet_loss: float,
    utilization: float,
    status_down: bool = False
) -> Dict[str, Any]:
    """
    Computes a risk score (0-100) for a tunnel based on metric conditions and status.
    """
    if status_down:
        return {
            "entity_id": tunnel_id,
            "entity_type": "tunnel",
            "risk_score": 100,
            "risk_level": "high",
            "signals": ["tunnel_down"]
        }

    # Weights: loss: 50%, latency: 30%, utilization: 20%
    loss_contrib = min(50.0, packet_loss * 10.0)      # Max 50 points if loss >= 5%
    latency_contrib = min(30.0, max(0.0, (latency - 30.0) * 0.3))  # Max 30 points if latency >= 130ms
    util_contrib = min(20.0, max(0.0, (utilization - 75.0) * 0.8))  # Max 20 points if util >= 100%

    score = int(loss_contrib + latency_contrib + util_contrib)
    score = min(100, max(0, score))

    signals = []
    if packet_loss >= 1.0:
        signals.append("packet_loss")
    if latency >= 75.0:
        signals.append("high_latency")
    if utilization >= 80.0:
        signals.append("increasing_utilization")

    level = "low"
    if score >= 76:
        level = "high"
    elif score >= 51:
        level = "elevated"
    elif score >= 26:
        level = "moderate"

    return {
        "entity_id": tunnel_id,
        "entity_type": "tunnel",
        "risk_score": score,
        "risk_level": level,
        "signals": signals
    }

def calculate_site_risk(
    site_id: str,
    tunnel_risks: List[int],
    event_count: int,
    device_health_degraded: bool = False
) -> Dict[str, Any]:
    """
    Aggregates tunnel risk scores and system events to compute site risk index.
    """
    if not tunnel_risks:
        avg_tunnel_risk = 0.0
    else:
        avg_tunnel_risk = sum(tunnel_risks) / len(tunnel_risks)

    # Event penalty: 5 points per event, max 30
    event_penalty = min(30.0, event_count * 5.0)
    
    # Device state penalty: 20 points
    dev_penalty = 20.0 if device_health_degraded else 0.0

    score = int(avg_tunnel_risk * 0.6 + event_penalty + dev_penalty)
    score = min(100, max(0, score))

    level = "low"
    if score >= 76:
        level = "high"
    elif score >= 51:
        level = "elevated"
    elif score >= 26:
        level = "moderate"

    signals = []
    if avg_tunnel_risk >= 50:
        signals.append("degraded_tunnels")
    if event_count > 3:
        signals.append("alarm_events_spike")
    if device_health_degraded:
        signals.append("device_hardware_warning")

    return {
        "entity_id": site_id,
        "entity_type": "site",
        "risk_score": score,
        "risk_level": level,
        "signals": signals
    }
