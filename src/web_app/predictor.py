import numpy as np
from sklearn.linear_model import LinearRegression

def predict_future(data, steps=10):
    if len(data) < 5:
        return None, None

    X = np.arange(len(data)).reshape(-1,1)
    y = np.array(data)

    model = LinearRegression()
    model.fit(X, y)

    future_x = np.arange(len(data), len(data)+steps).reshape(-1,1)
    future_y = model.predict(future_x)

    return future_x.flatten(), future_y