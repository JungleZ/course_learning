import mlflow
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

mlflow.set_experiment("customer-clustering")

np.random.seed(42)
n_samples = 300
X = np.random.rand(n_samples, 3) * 100
y_true = np.random.randint(0, 3, n_samples)

X_train, X_test, _, _ = train_test_split(X, y_true, test_size=0.2, random_state=42)

with mlflow.start_run():
    n_clusters = 3
    mlflow.log_param("n_clusters", n_clusters)
    mlflow.log_param("algorithm", "KMeans")
    
    model = KMeans(n_clusters=n_clusters, random_state=42)
    model.fit(X_train)
    
    labels = model.predict(X_test)
    silhouette = silhouette_score(X_test, labels)
    
    mlflow.log_metric("silhouette_score", silhouette)
    mlflow.sklearn.log_model(model, "model")
    
    print(f"Customer Clustering - Silhouette: {silhouette:.4f}")