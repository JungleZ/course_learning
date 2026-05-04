import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os

print("Training model...")

np.random.seed(42)

positive_words = ["great", "amazing", "excellent", "fantastic", "wonderful", "love", "best", "perfect", "awesome", "brilliant", "superb", "enjoyed", "recommend", "good", "nice", "terrific", "outstanding", "fabulous", "delightful", "impressive"]
negative_words = ["bad", "terrible", "horrible", "awful", "boring", "worst", "poor", "hate", "dislike", "waste", "disappointing", "dull", "mediocre", "pathetic", "lousy", "stupid", "annoying", "disgusting", "unwatchable", "ridiculous"]

n_samples = 5000
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

def clean_text(text):
    return re.sub(r'[^a-z\s]', '', str(text).lower())

df["review_clean"] = df["review"].apply(clean_text)
df["review_length"] = df["review_clean"].apply(lambda x: len(x.split()))

tfidf = TfidfVectorizer(max_features=100, ngram_range=(1, 1), stop_words="english")
X_tfidf = tfidf.fit_transform(df["review_clean"]).toarray()
X_length = df[["review_length"]].values
X = np.hstack([X_tfidf, X_length])
y = df["sentiment"]

model = LogisticRegression(C=0.1, max_iter=1000, random_state=42)
model.fit(X, y)

os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/review_classifier.pkl")
joblib.dump(tfidf, "model/tfidf_vectorizer.pkl")

print("Model saved to model/")
print(f"  - model/review_classifier.pkl")
print(f"  - model/tfidf_vectorizer.pkl")