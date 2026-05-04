import re
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
import joblib
import os

print("="*60)
print("模型优化 v2 - 特征工程 + 多模型对比")
print("="*60)

mlflow.set_experiment("movie-rating-optimize-v2")
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

np.random.seed(42)

positive_words = [
    "great", "amazing", "excellent", "fantastic", "wonderful", "love", "best", "perfect",
    "awesome", "brilliant", "superb", "enjoyed", "recommend", "good", "nice", "terrific",
    "outstanding", "fabulous", "delightful", "impressive", "masterpiece", "phenomenal",
    "incredible", "spectacular", "magnificent", "sublime", "divine", "marvelous"
]

negative_words = [
    "bad", "terrible", "horrible", "awful", "boring", "worst", "poor", "hate", "dislike",
    "waste", "disappointing", "dull", "mediocre", "pathetic", "lousy", "stupid",
    "annoying", "disgusting", "unwatchable", "ridiculous", "dreadful", "miserable",
    "atrocious", "abysmal", "insufferable", "unbearable", "despicable"
]

# 20000 条数据
n_samples = 20000
reviews = []
sentiments = []

for i in range(n_samples):
    review_length = np.random.randint(5, 15)
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

def clean_text(text):
    return re.sub(r'[^a-z\s]', '', str(text).lower())

df["review_clean"] = df["review"].apply(clean_text)
df["review_length"] = df["review_clean"].apply(lambda x: len(x.split()))
df["word_count"] = df["review_clean"].apply(lambda x: len(x))
df["exclamation"] = df["review"].apply(lambda x: x.count('!'))
df["question"] = df["review"].apply(lambda x: x.count('?'))

# 特征配置
feature_configs = [
    {"name": "tfidf-100-1gram", "max_features": 100, "ngram": (1, 1), "add_features": False},
    {"name": "tfidf-200-2gram", "max_features": 200, "ngram": (1, 2), "add_features": False},
    {"name": "tfidf-300-3gram", "max_features": 300, "ngram": (1, 3), "add_features": False},
    {"name": "tfidf-200-2gram+meta", "max_features": 200, "ngram": (1, 2), "add_features": True},
]

# 模型配置
model_configs = [
    {"name": "LogisticRegression-C0.1", "model": lambda: LogisticRegression(C=0.1, max_iter=1000, random_state=42)},
    {"name": "LogisticRegression-C1.0", "model": lambda: LogisticRegression(C=1.0, max_iter=1000, random_state=42)},
    {"name": "RandomForest-100", "model": lambda: RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)},
    {"name": "RandomForest-200", "model": lambda: RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)},
    {"name": "GradientBoosting", "model": lambda: GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)},
]

results = []
best_score = 0
best_config = None

for feat_cfg in feature_configs:
    print(f"\n[特征] {feat_cfg['name']}")

    tfidf = TfidfVectorizer(max_features=feat_cfg['max_features'], ngram_range=feat_cfg['ngram'], stop_words="english")
    X_tfidf = tfidf.fit_transform(df["review_clean"]).toarray()

    if feat_cfg['add_features']:
        meta_features = df[["review_length", "word_count", "exclamation", "question"]].values
        X = np.hstack([X_tfidf, meta_features])
    else:
        X = X_tfidf

    y = df["sentiment"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    for model_cfg in model_configs:
        print(f"  └── 训练 {model_cfg['name']}...", end=" ")

        model = model_cfg['model']()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)

        results.append({
            "feature": feat_cfg['name'],
            "model": model_cfg['name'],
            "accuracy": accuracy,
            "f1": f1,
            "auc": auc
        })

        # MLflow 记录
        with mlflow.start_run(run_name=f"{feat_cfg['name']}_{model_cfg['name']}"):
            mlflow.log_param("feature", feat_cfg['name'])
            mlflow.log_param("model", model_cfg['name'])
            mlflow.log_param("max_features", feat_cfg['max_features'])
            mlflow.log_param("ngram", f"{feat_cfg['ngram'][0]}-{feat_cfg['ngram'][1]}")
            mlflow.log_param("add_meta_features", feat_cfg['add_features'])

            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("f1_score", f1)
            mlflow.log_metric("auc_roc", auc)
            mlflow.sklearn.log_model(model, "model")

        print(f"ACC={accuracy:.4f}, F1={f1:.4f}, AUC={auc:.4f}")

        if auc > best_score:
            best_score = auc
            best_config = {
                "feature": feat_cfg,
                "model": model_cfg['name'],
                "model_fn": model_cfg['model']
            }

print("\n" + "="*60)
print("最佳配置:")
print(best_config)
print(f"最佳 AUC: {best_score:.4f}")
print("="*60)

# 用最佳配置重新训练并保存
print("\n用最佳配置训练最终模型...")
tfidf = TfidfVectorizer(max_features=best_config['feature']['max_features'],
                         ngram_range=best_config['feature']['ngram'],
                         stop_words="english")
X_tfidf = tfidf.fit_transform(df["review_clean"]).toarray()

if best_config['feature']['add_features']:
    meta_features = df[["review_length", "word_count", "exclamation", "question"]].values
    X = np.hstack([X_tfidf, meta_features])
else:
    X = X_tfidf

y = df["sentiment"]
final_model = best_config['model_fn']()
final_model.fit(X, y)

os.makedirs("model", exist_ok=True)
joblib.dump(final_model, "model/review_classifier_best.pkl")
joblib.dump(tfidf, "model/tfidf_vectorizer_best.pkl")

print("最佳模型已保存!")
print("\n=== 所有实验结果 ===")
for r in sorted(results, key=lambda x: x['auc'], reverse=True):
    print(f"{r['feature']} + {r['model']}: AUC={r['auc']:.4f}")