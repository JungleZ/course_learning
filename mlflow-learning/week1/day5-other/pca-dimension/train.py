import os
import mlflow

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error

mlflow.set_experiment("pca-dimensionality-reduction")

# 1. 读取数据
df = pd.read_csv("../../../data/raw/pca_data.csv")
X = df.values

# 2. 处理数据
X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

with mlflow.start_run():
    n_components = 3
    mlflow.log_param("n_components", n_components)
    mlflow.log_param("algorithm", "PCA")

    model = PCA(n_components=n_components)
    X_transformed = model.fit_transform(X_train)
    X_reconstructed = model.inverse_transform(X_transformed)

    mse = mean_squared_error(X_train, X_reconstructed)
    explained_variance = np.sum(model.explained_variance_ratio_)

    mlflow.log_metric("reconstruction_mse", mse)
    mlflow.log_metric("explained_variance_ratio", explained_variance)
    mlflow.sklearn.log_model(model, "model")

    print(f"PCA Dimensionality Reduction - MSE: {mse:.4f}, Explained Variance: {explained_variance:.4f}")