import re
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
import joblib
import os

print("="*50)
print("训练 20000 条数据的模型")
print("="*50)

# 设置 MLflow
mlflow.set_experiment("movie-rating-20k")
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

np.random.seed(42)

# 更多样化的词汇库
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

# 生成 20000 条数据
n_samples = 20000
reviews = []
sentiments = []

print(f"生成 {n_samples} 条数据...")

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

    # 10% 噪声
    if np.random.random() < 0.1:
        sentiment_score = -sentiment_score

    review = " ".join(words)
    reviews.append(review)

    if sentiment_score > 0 and np.random.random() > 0.05:
        sentiments.append(1)
    else:
        sentiments.append(0)

df = pd.DataFrame({"review": reviews, "sentiment": sentiments})

print(f"数据生成完成! 正面: {sum(sentiments)}, 负面: {n_samples - sum(sentiments)}")

# 清洗文本
def clean_text(text):
    return re.sub(r'[^a-z\s]', '', str(text).lower())

df["review_clean"] = df["review"].apply(clean_text)
df["review_length"] = df["review_clean"].apply(lambda x: len(x.split()))

# 特征工程
print("特征工程...")
tfidf = TfidfVectorizer(max_features=200, ngram_range=(1, 2), stop_words="english")
X_tfidf = tfidf.fit_transform(df["review_clean"]).toarray()
X_length = df[["review_length"]].values
X = np.hstack([X_tfidf, X_length])
y = df["sentiment"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"训练集: {len(X_train)}, 测试集: {len(X_test)}")

# 训练模型
print("训练模型...")

with mlflow.start_run(run_name="logistic-20k"):
    mlflow.log_param("model", "LogisticRegression")
    mlflow.log_param("C", 0.1)
    mlflow.log_param("n_samples", n_samples)
    mlflow.log_param("max_features", 200)
    mlflow.log_param("ngram", "1-2")

    model = LogisticRegression(C=0.1, max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)

    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("auc_roc", auc)
    mlflow.sklearn.log_model(model, "model")

print("="*50)
print("训练完成!")
print(f"Accuracy: {accuracy:.4f}")
print(f"F1 Score: {f1:.4f}")
print(f"AUC-ROC: {auc:.4f}")
print("="*50)

# 保存模型
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/review_classifier_20k.pkl")
joblib.dump(tfidf, "model/tfidf_vectorizer_20k.pkl")
print("\n模型已保存到 model/ 目录")