import mlflow
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

mlflow.set_experiment("house-price-regression")

np.random.seed(42)
n_samples = 500
X = np.random.rand(n_samples, 4) * 100
y = 50 * X[:, 0] + 30 * X[:, 1] + 20 * X[:, 2] + 10 * X[:, 3] + np.random.randn(n_samples) * 10

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

with mlflow.start_run():
    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_param("n_features", 4)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    mlflow.log_metric("mse", mse)
    mlflow.log_metric("rmse", np.sqrt(mse))
    mlflow.log_metric("r2_score", r2)
    mlflow.sklearn.log_model(model, "model")
    
    print(f"House Price Regression - MSE: {mse:.2f}, R2: {r2:.4f}")