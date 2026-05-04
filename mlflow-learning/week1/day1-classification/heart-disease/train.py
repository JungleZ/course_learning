import os
import mlflow

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score

mlflow.set_experiment("heart-disease-classification")

# 1. 读取数据
df = pd.read_csv("../../../data/raw/heart_disease.csv")
X = df.drop("target", axis=1)
y = df["target"]

# 2. 处理数据
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

with mlflow.start_run():
    mlflow.log_param("model_type", "LogisticRegression")
    mlflow.log_param("solver", "lbfgs")
    mlflow.log_param("max_iter", 200)

    model = LogisticRegression(solver='lbfgs', max_iter=200, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')

    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    mlflow.sklearn.log_model(model, "model")

    print(f"Heart Disease Classification - Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")