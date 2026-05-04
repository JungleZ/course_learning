import os
import mlflow

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report

mlflow.set_experiment("sklearn-mnist-digits")

print("="*50)
print("手写数字识别 (Digits 数据集)")
print("="*50)

# 加载数据
digits = load_digits()
X = digits.data
y = digits.target

print(f"数据形状: {X.shape}")
print(f"类别数: {len(np.unique(y))}")

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"训练集: {len(X_train)} 样本")
print(f"测试集: {len(X_test)} 样本")

# 标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\n" + "="*50)
print("训练神经网络...")
print("="*50)

with mlflow.start_run(run_name="mlp-digits"):
    mlflow.log_param("model", "MLPClassifier")
    mlflow.log_param("hidden_layers", "(100, 50)")
    mlflow.log_param("activation", "relu")
    mlflow.log_param("max_iter", 500)

    model = MLPClassifier(
        hidden_layer_sizes=(100, 50),
        activation='relu',
        max_iter=500,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1
    )

    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)

    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(model, "model")

print(f"\n测试集准确率: {accuracy:.4f}")
print("\n分类报告:")
print(classification_report(y_test, y_pred))