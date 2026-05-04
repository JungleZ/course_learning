import sys
import os
sys.path.append(os.path.abspath("../../../../src"))

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import mlflow
import mlflow.sklearn

df = pd.read_csv("data/raw/iris.csv")
X = df.drop("target", axis=1)
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

mlflow.set_experiment("my-first-exp")

with mlflow.start_run():
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    mlflow.log_params({
        "max_iter": 1000,
        "test_size": 0.2,
        "random_state": 42
    })
    mlflow.log_metric("accuracy", acc)

    mlflow.sklearn.log_model(model, "model")
    print(f"训练完成，测试集准确率: {acc:.2%}")