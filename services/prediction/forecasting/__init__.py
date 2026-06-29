from typing import List, Dict, Any, Tuple
import time

def fit_linear_trend(x: List[float], y: List[float]) -> Tuple[float, float]:
    """
    Fits a linear trend line y = alpha + beta * x.
    Returns (alpha, beta). If x has 0 variance or fewer than 2 points, returns (y[-1], 0.0).
    """
    n = len(x)
    if n < 2:
        val = y[0] if n == 1 else 0.0
        return val, 0.0
        
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    num = 0.0
    den = 0.0
    for i in range(n):
        num += (x[i] - mean_x) * (y[i] - mean_y)
        den += (x[i] - mean_x) ** 2
        
    if den == 0.0:
        return mean_y, 0.0
        
    beta = num / den
    alpha = mean_y - beta * mean_x
    return alpha, beta

def forecast_metric(historical_values: List[float], historical_times: List[float], current_time: float) -> Dict[str, float]:
    """
    Forecasts a metric value at +15m, +30m, and +60m.
    Returns a dictionary of current and forecasted values.
    """
    if not historical_values:
        return {"current": 0.0, "forecast_15m": 0.0, "forecast_30m": 0.0, "forecast_60m": 0.0, "confidence": 0.5}
        
    current = historical_values[-1]
    
    alpha, beta = fit_linear_trend(historical_times, historical_values)
    
    # 15m = 900s, 30m = 1800s, 60m = 3600s
    f15 = max(0.0, alpha + beta * (current_time + 900))
    f30 = max(0.0, alpha + beta * (current_time + 1800))
    f60 = max(0.0, alpha + beta * (current_time + 3600))
    
    # If metric is utilization, cap it at 100%
    # (or let it exceed if desired, but clamping is more realistic)
    
    # Calculate confidence based on variance/deviation (or constant for simplicity)
    confidence = 0.85
    if len(historical_values) >= 5:
        # Standard deviation can lower confidence if data is highly scattered
        mean = sum(historical_values) / len(historical_values)
        variance = sum((v - mean) ** 2 for v in historical_values) / len(historical_values)
        if variance > 100.0:
            confidence = 0.65
            
    return {
        "current": round(current, 2),
        "forecast_15m": round(f15, 2),
        "forecast_30m": round(f30, 2),
        "forecast_60m": round(f60, 2),
        "confidence": confidence
    }
