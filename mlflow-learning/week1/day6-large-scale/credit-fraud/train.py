import os
import mlflow

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

mlflow.set_experiment("credit-fraud-detection")

print("="*50)
print("1. 读取数据")
print("="*50)
df = pd.read_csv("../../../data/raw/credit_fraud.csv")
print(f"数据形状: {df.shape}")
print(f"类别分布:\n{df['target'].value_counts()}")
print(f"欺诈比例: {df['target'].mean()*100:.2f}%")

print("\n" + "="*50)
print("2. 处理数据")
print("="*50)
X = df.drop("target", axis=1)
y = df["target"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"训练集: {X_train.shape[0]} 样本")
print(f"测试集: {X_test.shape[0]} 样本")
print(f"训练集欺诈比例: {y_train.mean()*100:.2f}%")
print(f"测试集欺诈比例: {y_test.mean()*100:.2f}%")

print("\n" + "="*50)
print("3. 模型训练")
print("="*50)
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1, class_weight='balanced')
model.fit(X_train, y_train)
print("训练完成!")

print("\n" + "="*50)
print("4. MLflow 记录")
print("="*50)
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)

with mlflow.start_run():
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    mlflow.log_param("class_weight", "balanced")
    mlflow.log_param("n_samples_train", len(X_train))
    mlflow.log_param("fraud_ratio_train", y_train.mean())

    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("auc_roc", auc)
    mlflow.sklearn.log_model(model, "model")

print(f"准确率: {accuracy:.4f}")
print(f"精确率: {precision:.4f}")
print(f"召回率: {recall:.4f}")
print(f"F1分数: {f1:.4f}")
print(f"AUC-ROC: {auc:.4f}")