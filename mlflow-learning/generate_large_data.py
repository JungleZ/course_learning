import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, make_regression
import os

os.makedirs("data/raw", exist_ok=True)

np.random.seed(42)

# 大规模分类数据 - 10000条，20个特征，4个类别
X, y = make_classification(n_samples=10000, n_features=20, n_classes=4, n_clusters_per_class=2, n_informative=5, random_state=42)
df_large_clf = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(20)])
df_large_clf['target'] = y
df_large_clf.to_csv("data/raw/large_classification.csv", index=False)

# 大规模回归数据 - 10000条，10个特征
X, y = make_regression(n_samples=10000, n_features=10, noise=10, random_state=42)
df_large_reg = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(10)])
df_large_reg['target'] = y
df_large_reg.to_csv("data/raw/large_regression.csv", index=False)

# 信用卡欺诈检测模拟 - 10000条
n_normal = 9000
n_fraud = 1000
X_normal = np.random.rand(n_normal, 15) * 100
X_fraud = np.random.rand(n_fraud, 15) * 100 + np.array([10, 20, 30, 0, 0, 50, 0, 0, 15, 25, 0, 0, 10, 0, 5])
X = np.vstack([X_normal, X_fraud])
y = np.array([0] * n_normal + [1] * n_fraud)
df_fraud = pd.DataFrame(X, columns=[f'transaction_{i}' for i in range(15)])
df_fraud['target'] = y
df_fraud.to_csv("data/raw/credit_fraud.csv", index=False)

# 用户行为数据 - 5000条
n_users = 5000
df_users = pd.DataFrame({
    'age': np.random.randint(18, 70, n_users),
    'income': np.random.randint(3000, 50000, n_users),
    'score': np.random.rand(n_users) * 100,
    'login_frequency': np.random.randint(1, 100, n_users),
    'session_duration': np.random.rand(n_users) * 3600,
    'pages_visited': np.random.randint(1, 50, n_users),
    'cart_value': np.random.rand(n_users) * 500,
    'target': np.random.randint(0, 3, n_users)
})
df_users.to_csv("data/raw/user_behavior.csv", index=False)

# 电影评分数据 - 8000条
n_movies = 8000
df_movies = pd.DataFrame({
    'budget': np.random.randint(100000, 200000000, n_movies),
    'runtime': np.random.randint(60, 240, n_movies),
    'vote_count': np.random.randint(100, 100000, n_movies),
    'popularity': np.random.rand(n_movies) * 100,
    'release_year': np.random.randint(1980, 2024, n_movies),
    'director_score': np.random.rand(n_movies) * 10,
    'actor_score': np.random.rand(n_movies) * 10,
    'target': np.random.rand(n_movies) * 10
})
df_movies.to_csv("data/raw/movie_rating.csv", index=False)

print("Large datasets created!")
print("  - large_classification.csv: 10000 rows, 20 features, 5 classes")
print("  - large_regression.csv: 10000 rows, 10 features")
print("  - credit_fraud.csv: 10000 rows (9000 normal, 1000 fraud)")
print("  - user_behavior.csv: 5000 rows")
print("  - movie_rating.csv: 8000 rows")