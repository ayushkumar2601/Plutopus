import math
from typing import List, Dict, Any, Optional

def calculate_z_score(current_val: float, historical_vals: List[float]) -> float:
    """
    Computes the Z-Score of the current value relative to historical data points.
    """
    n = len(historical_vals)
    if n < 3:
        return 0.0
        
    mean = sum(historical_vals) / n
    variance = sum((x - mean) ** 2 for x in historical_vals) / n
    std_dev = math.sqrt(variance)
    
    if std_dev == 0.0:
        return 0.0
        
    return abs(current_val - mean) / std_dev

def detect_anomaly(
    entity_id: str,
    entity_type: str,
    metric_name: str,
    current_val: float,
    historical_vals: List[float]
) -> Optional[Dict[str, Any]]:
    """
    Analyzes a metric value and flags anomalies based on Z-score thresholds.
    """
    if len(historical_vals) < 3:
        return None
        
    z = calculate_z_score(current_val, historical_vals)
    
    if z >= 2.5:
        severity = "critical" if z >= 4.0 else "warning"
        description = f"Sudden anomaly spike detected on {entity_type} {entity_id}. Z-Score: {z:.2f}."
        
        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "metric": metric_name,
            "severity": severity,
            "score": round(z, 2),
            "description": description
        }
    return None
