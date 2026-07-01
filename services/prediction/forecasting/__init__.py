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

def calculate_ema(values: List[float], alpha: float = 0.2) -> List[float]:
    if not values:
        return []
    ema = [values[0]]
    for v in values[1:]:
        ema.append(alpha * v + (1 - alpha) * ema[-1])
    return ema

def forecast_metric(metric_name: str, historical_values: List[float], historical_times: List[float], current_time: float) -> Dict[str, float]:
    """
    Forecasts a metric value using EMA smoothing and horizon-aware trend dampening.
    """
    if not historical_values:
        return {"current": 0.0, "forecast_15m": 0.0, "forecast_30m": 0.0, "forecast_60m": 0.0, "confidence": 0.5}
        
    current_raw = historical_values[-1]
    base_time = historical_times[-1]
    time_span = historical_times[-1] - historical_times[0] if len(historical_times) > 1 else 0.0
    
    # Phase 2: EMA Smoothing
    # Apply EMA to smooth out short-term spikes
    alpha_ema = 0.2
    ema_values = calculate_ema(historical_values, alpha=alpha_ema)
    current_smoothed = ema_values[-1]
    
    # Normalize timestamps to relative seconds
    normalized_times = [t - base_time for t in historical_times]
    
    # Extract trend from EMA series
    trend_intercept, trend_slope = fit_linear_trend(normalized_times, ema_values)
    
    # Phase 3: Multi-Horizon Trend Forecasting
    # Horizon-aware dampening (trend decays over time)
    # 15m dampening: 0.8, 30m dampening: 0.5, 60m dampening: 0.2
    damp_15 = 0.8
    damp_30 = 0.5
    damp_60 = 0.2
    
    raw_delta_15 = trend_slope * 900 * damp_15
    raw_delta_30 = trend_slope * 1800 * damp_30
    raw_delta_60 = trend_slope * 3600 * damp_60
    
    if metric_name == "latency":
        max_increase_15 = current_smoothed * 0.50
        max_increase_30 = current_smoothed * 1.00
        max_increase_60 = current_smoothed * 2.00
        max_decrease = current_smoothed * 0.50
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
        
    delta_15 = max(min(raw_delta_15, max_increase_15), -max_decrease)
    delta_30 = max(min(raw_delta_30, max_increase_30), -max_decrease * 1.5)
    delta_60 = max(min(raw_delta_60, max_increase_60), -max_decrease * 2.0)
    
    # Forecasts based on smoothed current level
    f15_raw = current_smoothed + delta_15
    f30_raw = current_smoothed + delta_30
    f60_raw = current_smoothed + delta_60
    
    f15 = max(min_val, min(max_val, f15_raw))
    f30 = max(min_val, min(max_val, f30_raw))
    f60 = max(min_val, min(max_val, f60_raw))
    
    # Diagnostic Log
    import logging
    logger = logging.getLogger("prediction-worker")
    logger.info(f"DIAGNOSTIC: metric={metric_name}, cur_raw={current_raw:.2f}, cur_ema={current_smoothed:.2f}, slope={trend_slope:.4f}, delta15={delta_15:.4f}, f15={f15:.4f}")
    
    # Phase 4: Quantitative Confidence Scoring
    # Base calculation using sample size, historical coverage, and variance
    n = len(historical_values)
    
    # 1. Sample Size Score (ideal >= 60 samples)
    size_score = min(n / 60.0, 1.0)
    
    # 2. Coverage Score (ideal >= 900s or 15m)
    coverage_score = min(time_span / 900.0, 1.0)
    
    # 3. Variance Score (lower variance = higher confidence)
    if n > 1:
        mean = sum(historical_values) / n
        variance = sum((v - mean) ** 2 for v in historical_values) / n
        var_score = 1.0 / (1.0 + (variance / 100.0))
    else:
        var_score = 0.0
        
    # 4. Horizon Penalty (Since this DB schema stores a single confidence for all horizons,
    # we penalize the overall confidence based on the furthest projection: 60m)
    horizon_penalty = 0.85
    
    # Final mathematical confidence
    confidence = ((0.4 * size_score) + (0.4 * coverage_score) + (0.2 * var_score)) * horizon_penalty
    confidence = max(min(confidence, 1.0), 0.0)
    
    return {
        "current": round(current_raw, 2),
        "forecast_15m": round(f15, 2),
        "forecast_30m": round(f30, 2),
        "forecast_60m": round(f60, 2),
        "confidence": round(confidence, 2)
    }

