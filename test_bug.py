import time
from typing import List, Tuple

def fit_linear_trend(x: List[float], y: List[float]) -> Tuple[float, float]:
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

# Simulate
now = time.time()
times = [now - 60, now - 50, now - 40, now - 30, now - 20, now - 10, now]
vals = [10.0, 12.0, 15.0, 14.0, 18.0, 20.0, 25.0]

alpha, beta = fit_linear_trend(times, vals)
print(f"alpha: {alpha}, beta: {beta}")
f15 = max(0.0, alpha + beta * (now + 900))
print(f"f15: {f15}")

