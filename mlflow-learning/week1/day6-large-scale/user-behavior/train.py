import os
import mlflow

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

mlflow.set_experiment("user-behavior-clustering")

print("="*50)
print("1. 读取数据")
print("="*50)
df = pd.read_csv("../../../data/raw/user_behavior.csv")
print(f"数据形状: {df.shape}")
print(f"用户分组:\n{df['target'].value_counts()}")

print("\n" + "="*50)
print("2. 处理数据")
print("="*50)
X = df.drop("target", axis=1)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"特征数量: {X.shape[1]}")

print("\n" + "="*50)
print("3. 模型训练")
print("="*50)
n_clusters = 3
model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
labels = model.fit_predict(X_scaled)
silhouette = silhouette_score(X_scaled, labels)
print(f"聚类完成! 轮廓系数: {silhouette:.4f}")

print("\n" + "="*50)
print("4. MLflow 记录")
print("="*50)
with mlflow.start_run():
    mlflow.log_param("algorithm", "KMeans")
    mlflow.log_param("n_clusters", n_clusters)
    mlflow.log_param("n_samples", len(X))
    mlflow.log_param("n_features", X.shape[1])

    mlflow.log_metric("silhouette_score", silhouette)
    mlflow.sklearn.log_model(model, "model")
    mlflow.sklearn.log_model(scaler, "scaler")

print("聚类分布:")
for i in range(n_clusters):
    print(f"  Cluster {i}: {(labels == i).sum()} 用户")