"""
Day 8: Docker 容器化部署 - Flask API 应用

功能：与 Day 3 的 Flask 应用类似，但优化为 Docker 部署
"""

from flask import Flask, request, jsonify
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib
import numpy as np
import os

app = Flask(__name__)

# 模型路径
MODEL_PATH = os.environ.get("MODEL_PATH", "iris_model.pkl")
CLASS_NAMES = ["setosa", "versicolor", "virginica"]

# 启动时加载或训练模型
def get_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    
    # 模型不存在则训练
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )
    model = DecisionTreeClassifier(max_depth=3, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)
    return model

model = get_model()
print(f"✅ 模型已加载，路径：{MODEL_PATH}")


@app.route("/")
def home():
    return jsonify({
        "service": "Iris Classifier API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "GET - 健康检查",
            "/predict": "POST - 预测鸢尾花品种",
            "/info": "GET - 模型信息"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model_loaded": model is not None})


@app.route("/info", methods=["GET"])
def info():
    return jsonify({
        "model_type": "DecisionTreeClassifier",
        "classes": CLASS_NAMES,
        "n_features": 4,
        "feature_names": ["sepal_length", "sepal_width", "petal_length", "petal_width"]
    })


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        if "features" not in data:
            return jsonify({"error": "请提供 features 字段"}), 400
        
        features = data["features"]
        if len(features) != 4:
            return jsonify({"error": "需要4个特征值"}), 400
        
        features_array = np.array([features], dtype=float)
        prediction = model.predict(features_array)[0]
        
        try:
            probabilities = model.predict_proba(features_array)[0]
            prob_dict = {CLASS_NAMES[i]: round(float(probabilities[i]), 4) for i in range(3)}
        except:
            prob_dict = {}
        
        return jsonify({
            "prediction": CLASS_NAMES[prediction],
            "class_id": int(prediction),
            "probabilities": prob_dict
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
