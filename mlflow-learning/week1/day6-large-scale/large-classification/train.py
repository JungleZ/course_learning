import os
import mlflow

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

mlflow.set_experiment("large-classification")

print("="*50)
print("1. 读取数据")
print("="*50)
df = pd.read_csv("../../../data/raw/large_classification.csv")
print(f"数据形状: {df.shape}")
print(f"类别分布:\n{df['target'].value_counts()}")

print("\n" + "="*50)
print("2. 处理数据")
print("="*50)
X = df.drop("target", axis=1)
y = df["target"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"训练集: {X_train.shape[0]} 样本")
print(f"测试集: {X_test.shape[0]} 样本")

print("\n" + "="*50)
print("3. 模型训练")
print("="*50)
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
print("训练完成!")

print("\n" + "="*50)
print("4. MLflow 记录")
print("="*50)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

with mlflow.start_run():
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    mlflow.log_param("n_samples_train", len(X_train))
    mlflow.log_param("n_features", X.shape[1])
    mlflow.log_param("n_classes", len(y.unique()))

    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(model, "model")

print(f"测试集准确率: {accuracy:.4f}")
print("\n分类报告:")
print(classification_report(y_test, y_pred))