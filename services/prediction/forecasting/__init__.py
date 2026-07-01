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

def forecast_metric(metric_name: str, historical_values: List[float], historical_times: List[float], current_time: float) -> Dict[str, float]:
    """
    Forecasts a metric value at +15m, +30m, and +60m using trend-limited forecasting.
    Returns a dictionary of current and forecasted values.
    """
    if not historical_values:
        return {"current": 0.0, "forecast_15m": 0.0, "forecast_30m": 0.0, "forecast_60m": 0.0, "confidence": 0.5}
        
    current = historical_values[-1]
    base_time = historical_times[-1]
    
    time_span = historical_times[-1] - historical_times[0] if len(historical_times) > 1 else 0.0
    
    # Normalize timestamps to relative seconds to avoid magnitude leakage
    normalized_times = [t - base_time for t in historical_times]
    alpha, beta = fit_linear_trend(normalized_times, historical_values)
    
    if metric_name == "latency":
        max_increase_15 = current * 0.50
        max_increase_30 = current * 1.00
        max_increase_60 = current * 2.00
        max_decrease = current * 0.50
        min_val = 0.0
        max_val = 5000.0
    elif metric_name == "utilization":
        max_increase_15 = 30.0
        max_increase_30 = 50.0
        max_increase_60 = 80.0
        max_decrease = 30.0
        min_val = 0.0
        max_val = 100.0
    else: # packet_loss
        max_increase_15 = 10.0
        max_increase_30 = 20.0
        max_increase_60 = 30.0
        max_decrease = 10.0
        min_val = 0.0
        max_val = 100.0
        
    # Evaluate at relative future intervals and cap the absolute jump
    delta_15 = max(min(beta * 900, max_increase_15), -max_decrease)
    delta_30 = max(min(beta * 1800, max_increase_30), -max_decrease * 1.5)
    delta_60 = max(min(beta * 3600, max_increase_60), -max_decrease * 2.0)
    
    f15_raw = current + delta_15
    f30_raw = current + delta_30
    f60_raw = current + delta_60
    
    # Cap values based on physical bounds
    f15 = max(min_val, min(max_val, f15_raw))
    f30 = max(min_val, min(max_val, f30_raw))
    f60 = max(min_val, min(max_val, f60_raw))
    
    # Diagnostic Log
    import logging
    logger = logging.getLogger("prediction-worker")
    logger.info(f"DIAGNOSTIC: metric={metric_name}, current={current:.2f}, window={time_span:.1f}s, slope={beta:.4f}, raw_delta={beta*900:.4f}, delta15={delta_15:.4f}, f15_capped={f15:.4f}")
    
    # Calculate confidence
    confidence = 0.85
    if len(historical_values) >= 5:
        mean = sum(historical_values) / len(historical_values)
        variance = sum((v - mean) ** 2 for v in historical_values) / len(historical_values)
        if variance > 100.0 or time_span < 60.0:
            confidence = 0.65
            
    return {
        "current": round(current, 2),
        "forecast_15m": round(f15, 2),
        "forecast_30m": round(f30, 2),
        "forecast_60m": round(f60, 2),
        "confidence": confidence
    }

