import os
import mlflow

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

mlflow.set_experiment("movie-rating-prediction")

print("="*50)
print("1. 读取数据")
print("="*50)
df = pd.read_csv("../../../data/raw/movie_rating.csv")
print(f"数据形状: {df.shape}")
print(f"评分范围: {df['target'].min():.2f} - {df['target'].max():.2f}")

print("\n" + "="*50)
print("2. 处理数据")
print("="*50)
X = df.drop("target", axis=1)
y = df["target"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"训练集: {X_train.shape[0]} 电影")
print(f"测试集: {X_test.shape[0]} 电影")

print("\n" + "="*50)
print("3. 模型训练")
print("="*50)
model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
print("训练完成!")

print("\n" + "="*50)
print("4. MLflow 记录")
print("="*50)
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

with mlflow.start_run():
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 15)
    mlflow.log_param("n_movies_train", len(X_train))

    mlflow.log_metric("mse", mse)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("r2_score", r2)
    mlflow.sklearn.log_model(model, "model")

print(f"RMSE: {rmse:.4f}")
print(f"MAE: {mae:.4f}")
print(f"R2 Score: {r2:.4f}")

feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print("\nTop 5 重要特征:")
print(feature_importance.head())