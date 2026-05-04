import pandas as pd
import numpy as np
import re
import sys
import warnings
warnings.filterwarnings('ignore')

# 解决 Windows 编码
sys.stdout.reconfigure(encoding='utf-8')

import mlflow
import mlflow.sklearn

# =====================
# MLflow
# =====================
mlflow.set_experiment("movie-rating-prediction")

# =====================
# 生成 5000 条更真实的影评数据
# =====================
print("Loading dataset...")

n_samples = 5000

# 更多样化的评论词汇
positive_words = ["great", "amazing", "excellent", "fantastic", "wonderful", "love", "best", "perfect", "awesome", "brilliant", "superb", "enjoyed", "recommend", "good", "nice", "terrific", "outstanding", "fabulous", "delightful", "impressive"]
negative_words = ["bad", "terrible", "horrible", "awful", "boring", "worst", "poor", "hate", "dislike", "waste", "disappointing", "dull", "mediocre", "pathetic", "lousy", "stupid", "annoying", "disgusting", "unwatchable", "ridiculous"]

reviews = []
sentiments = []

for i in range(n_samples):
    # 随机生成评论句子
    review_length = np.random.randint(3, 10)
    words = []
    sentiment_score = 0

    # 70% 正面, 30% 负面倾向
    is_positive = np.random.random() < 0.7

    for _ in range(review_length):
        if is_positive:
            word = np.random.choice(positive_words)
            sentiment_score += 1
        else:
            word = np.random.choice(negative_words)
            sentiment_score -= 1
        words.append(word)

    # 添加一些噪声：不是所有明显正面的评论都标记为1
    # 10% 的数据标签反转（模拟标注错误）
    if np.random.random() < 0.1:
        sentiment_score = -sentiment_score

    review = " ".join(words)
    reviews.append(review)

    # 情感得分转标签（加入随机性）
    if sentiment_score > 0 and np.random.random() > 0.05:
        sentiments.append(1)
    else:
        sentiments.append(0)

df = pd.DataFrame({"review": reviews, "sentiment": sentiments})

# 文本清洗
def clean_text(text):
    return re.sub(r'[^a-z\s]', '', str(text).lower())

df["review"] = df["review"].apply(clean_text)

# TF-IDF 特征
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer(max_features=500, stop_words="english")
X = tfidf.fit_transform(df["review"]).toarray()
y = df["sentiment"]

# 划分数据集
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =====================
# 训练模型
# =====================
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

with mlflow.start_run(run_name="random-forest-5000-samples"):
    mlflow.log_param("model", "RandomForest")
    mlflow.log_param("samples", n_samples)
    mlflow.log_param("tfidf_max_features", 500)
    mlflow.log_param("noise_ratio", 0.1)

    print("Start training...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    mlflow.log_metric("mae", mae)
    mlflow.log_metric("mse", mse)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)

    mlflow.sklearn.log_model(model, "model")

    print("\nTraining finished!")
    print(f"MAE:  {mae:.4f}")
    print(f"MSE:  {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2:   {r2:.4f}")
    print("\nAll data logged to MLflow!")