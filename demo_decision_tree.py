import mlflow
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

mlflow.set_experiment("loan-approval-decision-tree")

np.random.seed(42)
X = np.random.rand(500, 5)
y = (X[:, 0] * 0.3 + X[:, 1] * 0.3 + X[:, 2] * 0.2 + np.random.rand(500) * 0.2 > 0.5).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

with mlflow.start_run():
    mlflow.log_param("max_depth", 5)
    mlflow.log_param("criterion", "gini")
    
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(model, "model")
    
    print(f"Decision Tree - Accuracy: {accuracy:.4f}")