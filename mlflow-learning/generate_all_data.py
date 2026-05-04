import pandas as pd
import numpy as np
from sklearn.datasets import load_iris, make_blobs
import os

os.makedirs("data/raw", exist_ok=True)

np.random.seed(42)

# 1. Heart Disease Data
X, y = make_blobs(n_samples=500, n_features=10, random_state=42)
df_heart = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(10)])
df_heart['target'] = y
df_heart.to_csv("data/raw/heart_disease.csv", index=False)

# 2. Loan Approval Data
X = np.random.rand(500, 5)
df_loan = pd.DataFrame(X, columns=['income','credit_score','employment_years','debt_ratio','asset_value'])
df_loan['target'] = (X[:, 0] * 0.3 + X[:, 1] * 0.3 + X[:, 2] * 0.2 + np.random.rand(500) * 0.2 > 0.5).astype(int)
df_loan.to_csv("data/raw/loan_approval.csv", index=False)

# 3. Image Classification Data
X, y = make_blobs(n_samples=300, centers=2, n_features=100, random_state=42)
df_image = pd.DataFrame(X, columns=[f'pixel_{i}' for i in range(100)])
df_image['target'] = y
df_image.to_csv("data/raw/image_classification.csv", index=False)

# 4. Iris Data
iris = load_iris()
df_iris = pd.DataFrame(iris.data, columns=iris.feature_names)
df_iris['target'] = iris.target
df_iris.to_csv("data/raw/iris.csv", index=False)

# 5. Iris Complete
df_iris.to_csv("data/raw/iris_complete.csv", index=False)

# 6. House Price Data
n_samples = 500
X = np.random.rand(n_samples, 4) * 100
df_house = pd.DataFrame(X, columns=['area','rooms','age','distance'])
df_house['price'] = 50 * X[:, 0] + 30 * X[:, 1] + 20 * X[:, 2] + 10 * X[:, 3] + np.random.randn(n_samples) * 10
df_house.to_csv("data/raw/house_price.csv", index=False)

# 7. Customer Clustering Data
n_samples = 300
X = np.random.rand(n_samples, 3) * 100
df_customer = pd.DataFrame(X, columns=['income','spending','recency'])
df_customer['target'] = np.random.randint(0, 3, n_samples)
df_customer.to_csv("data/raw/customer.csv", index=False)

# 8. PCA Data
n_samples = 200
X = np.random.rand(n_samples, 10) * 50 + np.random.randn(n_samples, 10) * 5
df_pca = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(10)])
df_pca.to_csv("data/raw/pca_data.csv", index=False)

print("All data files created!")