import os
import mlflow

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

mlflow.set_experiment("image-classification-svm")

# 1. 读取数据
df = pd.read_csv("../../../data/raw/image_classification.csv")
X = df.drop("target", axis=1)
y = df["target"]

# 2. 处理数据
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

with mlflow.start_run():
    mlflow.log_param("kernel", "rbf")
    mlflow.log_param("C", 1.0)

    model = SVC(kernel='rbf', C=1.0, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(model, "model")

    print(f"SVM Classification - Accuracy: {accuracy:.4f}")