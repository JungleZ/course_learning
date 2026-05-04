import os
import mlflow

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

mlflow.set_experiment("customer-clustering")

# 1. 读取数据
df = pd.read_csv("../../../data/raw/customer.csv")
X = df.drop("target", axis=1)

# 2. 处理数据 (聚类不需要y)
X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

with mlflow.start_run():
    n_clusters = 3
    mlflow.log_param("n_clusters", n_clusters)
    mlflow.log_param("algorithm", "KMeans")

    model = KMeans(n_clusters=n_clusters, random_state=42)
    model.fit(X_train)

    labels = model.predict(X_test)
    silhouette = silhouette_score(X_test, labels)

    mlflow.log_metric("silhouette_score", silhouette)
    mlflow.sklearn.log_model(model, "model")

    print(f"Customer Clustering - Silhouette: {silhouette:.4f}")