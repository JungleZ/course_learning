import mlflow
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pandas as pd

mlflow.set_experiment("iris-classification-with-data")

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

train_df = pd.DataFrame(X_train, columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])
train_df['target'] = y_train

test_df = pd.DataFrame(X_test, columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])
test_df['target'] = y_test

with mlflow.start_run():
    n_estimators = 100
    max_depth = 5
    
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_param("train_size", len(X_train))
    mlflow.log_param("test_size", len(X_test))
    mlflow.log_param("n_features", X.shape[1])
    mlflow.log_param("n_classes", len(set(y)))
    
    clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(clf, "model")
    
    train_csv = "D:/code_workspaces/data/train.csv"
    test_csv = "D:/code_workspaces/data/test.csv"
    train_df.to_csv(train_csv, index=False)
    test_df.to_csv(test_csv, index=False)
    
    mlflow.log_artifact(train_csv, "data")
    mlflow.log_artifact(test_csv, "data")
    
    print(f"Train samples: {len(train_df)}, Test samples: {len(test_df)}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Logged datasets to MLflow!")