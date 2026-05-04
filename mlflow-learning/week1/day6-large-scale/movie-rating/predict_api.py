import re
import numpy as np
import joblib
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =====================
# 加载已训练好的模型
# =====================
print("Loading model from files...")

model = joblib.load("model/review_classifier_best.pkl")
tfidf = joblib.load("model/tfidf_vectorizer_best.pkl")

print("Model loaded successfully!")

def clean_text(text):
    return re.sub(r'[^a-z\s]', '', str(text).lower())

def predict_sentiment(text):
    text_clean = clean_text(text)
    text_length = len(text_clean.split())

    text_tfidf = tfidf.transform([text_clean]).toarray()
    X = np.hstack([text_tfidf, [[text_length]]])

    prob = model.predict_proba(X)[0]
    prediction = model.predict(X)[0]

    return {
        "sentiment": "positive" if prediction == 1 else "negative",
        "confidence": float(max(prob)),
        "positive_prob": float(prob[1]),
        "negative_prob": float(prob[0])
    }

# =====================
# API 接口
# =====================
@app.route('/')
def home():
    return send_file('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "请输入评论文本"}), 400

    result = predict_sentiment(text)
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("情感分析 API 已启动!")
    print("访问: http://localhost:5000")
    print("接口: POST /predict")
    print("="*50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)