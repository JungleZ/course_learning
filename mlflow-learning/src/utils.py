import mlflow

def log_experiment(params, metrics, model, model_name="model"):
    mlflow.log_params(params)
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(model, model_name)