import numpy as np
from sklearn.linear_model import LinearRegression


def predict_future(data, steps=10):
    if len(data) < 5:
        return None, None

    x_values = np.arange(len(data)).reshape(-1, 1)
    y_values = np.array(data, dtype=float)

    model = LinearRegression()
    model.fit(x_values, y_values)

    future_x = np.arange(len(data), len(data) + steps).reshape(-1, 1)
    future_y = np.clip(model.predict(future_x), 0, 100)

    return future_x.flatten().tolist(), np.round(future_y, 2).tolist()


def detect_anomaly(data, min_points=10, std_multiplier=2.0):
    series = np.array(data, dtype=float)
    if len(series) < max(min_points + 1, 2):
        return False, 0.0, 0.0

    baseline = series[:-1]
    current_value = float(series[-1])
    average = float(np.mean(baseline))
    standard_deviation = float(np.std(baseline))
    threshold = average + std_multiplier * standard_deviation

    return current_value > threshold, round(average, 2), round(threshold, 2)
