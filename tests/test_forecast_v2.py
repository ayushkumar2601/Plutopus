import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/prediction")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/prediction/src")))

from forecasting import forecast_metric

def test_stable_signal():
    hist_vals = [100.0, 101.0, 99.0, 100.0, 101.0]
    hist_times = [1.0, 2.0, 3.0, 4.0, 5.0]
    res = forecast_metric("latency", hist_vals, hist_times, 10.0)
    
    # Forecast should remain near 100
    assert 90.0 <= res["forecast_15m"] <= 120.0
    assert 90.0 <= res["forecast_60m"] <= 130.0

def test_sudden_spike():
    hist_vals = [100.0, 100.0, 100.0, 100.0, 500.0]
    hist_times = [1.0, 2.0, 3.0, 4.0, 5.0]
    res = forecast_metric("latency", hist_vals, hist_times, 10.0)
    
    # Forecast should not become 5000 instantly. EMA smooths the spike.
    assert res["forecast_15m"] < 1500.0

def test_gradual_trend():
    hist_vals = [10.0, 15.0, 20.0, 25.0, 30.0]
    hist_times = [1.0, 2.0, 3.0, 4.0, 5.0]
    res = forecast_metric("utilization", hist_vals, hist_times, 10.0)
    
    # Should continue trend smoothly.
    assert res["forecast_15m"] > 30.0

def test_missing_data():
    hist_vals = [100.0]
    hist_times = [1.0]
    res = forecast_metric("utilization", hist_vals, hist_times, 10.0)
    
    # With 1 point, no trend can be established. Should remain flat.
    assert res["forecast_15m"] == 100.0
    # Confidence should be heavily penalized (size=1, var=0, coverage=0)
    assert res["confidence"] < 0.5
