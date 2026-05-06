import os
import sys
import re
import numpy as np

# 添加mlflow-learning路径以便导入模型
sys.path.append(os.path.abspath('../../week6-large-scale/movie-rating'))

def load_sentiment_model():
    """加载情感分析模型"""
    try:
        import joblib
        model_path = '../../week6-large-scale/movie-rating/model/review_classifier_best.pkl'
        vectorizer_path = '../../week6-large-scale/movie-rating/model/tfidf_vectorizer_best.pkl'

        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            model = joblib.load(model_path)
            vectorizer = joblib.load(vectorizer_path)
            return model, vectorizer
    except Exception as e:
        print(f"加载情感分析模型失败: {e}")
    return None, None

# 初始化模型
_sentiment_model, _vectorizer = load_sentiment_model()

def clean_text(text):
    """清洗文本"""
    return re.sub(r'[^a-z\s]', '', str(text).lower())

def analyze_sentiment(text):
    """分析文本情感"""
    if not _sentiment_model or not _vectorizer:
        return {'sentiment': 'neutral', 'score': 0.5}

    text_clean = clean_text(text)
    X = _vectorizer.transform([text_clean]).toarray()

    # 添加简单特征
    text_length = len(text_clean.split())
    X = np.hstack([X, [[text_length]]])

    prob = _sentiment_model.predict_proba(X)[0]
    sentiment = 'positive' if prob[1] > 0.5 else 'negative'

    return {
        'sentiment': sentiment,
        'score': float(prob[1]),
        'positive_prob': float(prob[1]),
        'negative_prob': float(prob[0])
    }

if __name__ == '__main__':
    # 测试
    test_texts = [
        "You are so cute and amazing!",
        "I hate this app, it's terrible.",
        "The app is okay, nothing special."
    ]

    for text in test_texts:
        result = analyze_sentiment(text)
        print(f"文本: {text}")
        print(f"结果: {result}\n")
