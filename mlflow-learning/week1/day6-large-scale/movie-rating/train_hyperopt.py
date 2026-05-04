import pandas as pd
import numpy as np
import re
import sys
import warnings
warnings.filterwarnings('ignore')

sys.stdout.reconfigure(encoding='utf-8')

import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# =====================
# 1. 生成数据
# =====================
print("Loading dataset...")

n_samples = 5000
np.random.seed(42)

positive_words = ["great", "amazing", "excellent", "fantastic", "wonderful", "love", "best", "perfect", "awesome", "brilliant", "superb", "enjoyed", "recommend", "good", "nice", "terrific", "outstanding", "fabulous", "delightful", "impressive"]
negative_words = ["bad", "terrible", "horrible", "awful", "boring", "worst", "poor", "hate", "dislike", "waste", "disappointing", "dull", "mediocre", "pathetic", "lousy", "stupid", "annoying", "disgusting", "unwatchable", "ridiculous"]

reviews = []
sentiments = []

for i in range(n_samples):
    review_length = np.random.randint(3, 10)
    words = []
    sentiment_score = 0
    is_positive = np.random.random() < 0.7

    for _ in range(review_length):
        if is_positive:
            word = np.random.choice(positive_words)
            sentiment_score += 1
        else:
            word = np.random.choice(negative_words)
            sentiment_score -= 1
        words.append(word)

    if np.random.random() < 0.1:
        sentiment_score = -sentiment_score

    review = " ".join(words)
    reviews.append(review)

    if sentiment_score > 0 and np.random.random() > 0.05:
        sentiments.append(1)
    else:
        sentiments.append(0)

df = pd.DataFrame({"review": reviews, "sentiment": sentiments})

# =====================
# 2. 特征工程
# =====================
def clean_text(text):
    return re.sub(r'[^a-z\s]', '', str(text).lower())

df["review_clean"] = df["review"].apply(clean_text)
df["review_length"] = df["review_clean"].apply(lambda x: len(x.split()))

# =====================
# 3. 参数搜索空间
# =====================
param_grid = [
    {"model": "LogisticRegression", "C": 0.1, "max_features": 100, "ngram": 1},
    {"model": "LogisticRegression", "C": 1.0, "max_features": 200, "ngram": 1},
    {"model": "LogisticRegression", "C": 10.0, "max_features": 500, "ngram": 2},
    {"model": "RandomForest", "n_estimators": 50, "max_depth": 5, "max_features": 100, "ngram": 1},
    {"model": "RandomForest", "n_estimators": 100, "max_depth": 10, "max_features": 200, "ngram": 1},
    {"model": "RandomForest", "n_estimators": 200, "max_depth": 15, "max_features": 500, "ngram": 2},
    {"model": "GradientBoosting", "n_estimators": 50, "max_depth": 3, "max_features": 100, "ngram": 1},
    {"model": "GradientBoosting", "n_estimators": 100, "max_depth": 5, "max_features": 200, "ngram": 1},
]

# =====================
# 4. 遍历所有参数组合
# =====================
mlflow.set_experiment("movie-rating-hyperopt")

print(f"\n总共有 {len(param_grid)} 组参数要测试...\n")

best_score = 0
best_params = None
best_model = None

for i, params in enumerate(param_grid):
    print(f"[{i+1}/{len(param_grid)}] 测试: {params['model']} - C={params.get('C', 'N/A')}, n_estimators={params.get('n_estimators', 'N/A')}")

    # 创建特征
    tfidf = TfidfVectorizer(max_features=params['max_features'], ngram_range=(1, params['ngram']), stop_words="english")
    X_tfidf = tfidf.fit_transform(df["review_clean"]).toarray()

    X_length = df[["review_length"]].values
    X = np.hstack([X_tfidf, X_length])
    y = df["sentiment"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 训练模型
    if params["model"] == "LogisticRegression":
        model = LogisticRegression(C=params["C"], max_iter=1000, random_state=42)
    elif params["model"] == "RandomForest":
        model = RandomForestClassifier(n_estimators=params["n_estimators"], max_depth=params["max_depth"], random_state=42, n_jobs=-1)
    elif params["model"] == "GradientBoosting":
        model = GradientBoostingClassifier(n_estimators=params["n_estimators"], max_depth=params["max_depth"], random_state=42)

    model.fit(X_train, y_train)

    # 评估
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)

    # 记录到 MLflow
    with mlflow.start_run(run_name=f"{params['model']}_{i+1}"):
        mlflow.log_param("model_type", params["model"])
        mlflow.log_param("max_features", params["max_features"])
        mlflow.log_param("ngram", params["ngram"])

        if params["model"] == "LogisticRegression":
            mlflow.log_param("C", params["C"])
        elif params["model"] in ["RandomForest", "GradientBoosting"]:
            mlflow.log_param("n_estimators", params["n_estimators"])
            mlflow.log_param("max_depth", params["max_depth"])

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("auc_roc", auc)
        mlflow.sklearn.log_model(model, "model")

    print(f"   Accuracy: {accuracy:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}")

    # 记录最佳模型
    if auc > best_score:
        best_score = auc
        best_params = params
        best_model = model

print("\n" + "="*50)
print("最佳参数组合:")
print(best_params)
print(f"最佳 AUC: {best_score:.4f}")
print("="*50)