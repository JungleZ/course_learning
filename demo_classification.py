import mlflow
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score

mlflow.set_experiment("heart-disease-classification")

np.random.seed(42)
X, y = make_classification(n_samples=500, n_features=10, n_informative=5, n_redundant=2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

with mlflow.start_run():
    mlflow.log_param("model_type", "LogisticRegression")
    mlflow.log_param("solver", "lbfgs")
    mlflow.log_param("max_iter", 200)
    
    model = LogisticRegression(solver='lbfgs', max_iter=200, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    mlflow.sklearn.log_model(model, "model")
    
    print(f"Heart Disease Classification - Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")