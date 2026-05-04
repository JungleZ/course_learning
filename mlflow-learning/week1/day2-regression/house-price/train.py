import os
import mlflow

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

mlflow.set_experiment("house-price-regression")

# 1. 读取数据
df = pd.read_csv("../../../data/raw/house_price.csv")
X = df.drop("price", axis=1)
y = df["price"]

# 2. 处理数据
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

with mlflow.start_run():
    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_param("n_features", 4)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    mlflow.log_metric("mse", mse)
    mlflow.log_metric("rmse", np.sqrt(mse))
    mlflow.log_metric("r2_score", r2)
    mlflow.sklearn.log_model(model, "model")

    print(f"House Price Regression - MSE: {mse:.2f}, R2: {r2:.4f}")