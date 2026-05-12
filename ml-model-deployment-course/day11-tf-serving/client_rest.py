"""
Day 11: TF Serving REST API 客户端

通过 REST API 调用 TF Serving 进行预测

前提：TF Serving 已在 Docker 中运行
    docker run -d -p 8501:8501 -v <saved_model路径>:/models/iris_model -e MODEL_NAME=iris_model tensorflow/serving

运行方式：
    python client_rest.py
"""

import requests
import numpy as np
import json

TF_SERVING_URL = "http://localhost:8501/v1/models/iris_model"

# 加载预处理参数
script_dir = os.path.dirname(os.path.abspath(__file__))
import os
preprocessing_path = os.path.join(script_dir, "saved_model", "preprocessing.json")

try:
    with open(preprocessing_path, 'r') as f:
        preprocessing = json.load(f)
    scaler_mean = np.array(preprocessing["scaler_mean"])
    scaler_scale = np.array(preprocessing["scaler_scale"])
    CLASS_NAMES = preprocessing["class_names"]
except FileNotFoundError:
    print("⚠️ 预处理参数文件不存在，使用默认值")
    scaler_mean = np.zeros(4)
    scaler_scale = np.ones(4)
    CLASS_NAMES = ["setosa", "versicolor", "virginica"]


def preprocess(features):
    """标准化预处理"""
    return (np.array(features) - scaler_mean) / scaler_scale


def predict(features):
    """
    调用 TF Serving REST API 预测
    
    参数：
        features: list[float] - 4个特征值
    返回：
        dict - 预测结果
    """
    # 预处理
    scaled = preprocess(features)
    
    # 构建请求
    data = {
        "instances": [scaled.tolist()]
    }
    
    # 发送请求
    response = requests.post(
        f"{TF_SERVING_URL}:predict",
        json=data
    )
    
    if response.status_code != 200:
        return {"error": f"请求失败：{response.status_code}", "detail": response.text}
    
    result = response.json()
    predictions = result["predictions"][0]
    
    # 解析结果
    predicted_class = np.argmax(predictions)
    
    return {
        "prediction": CLASS_NAMES[predicted_class],
        "class_id": int(predicted_class),
        "probabilities": {CLASS_NAMES[i]: round(p, 4) for i, p in enumerate(predictions)}
    }


def predict_batch(samples):
    """批量预测"""
    scaled_samples = [preprocess(s).tolist() for s in samples]
    
    data = {"instances": scaled_samples}
    
    response = requests.post(
        f"{TF_SERVING_URL}:predict",
        json=data
    )
    
    if response.status_code != 200:
        return {"error": f"请求失败：{response.status_code}"}
    
    result = response.json()
    
    predictions = []
    for probs in result["predictions"]:
        predicted_class = np.argmax(probs)
        predictions.append({
            "prediction": CLASS_NAMES[predicted_class],
            "class_id": int(predicted_class),
            "probabilities": {CLASS_NAMES[i]: round(p, 4) for i, p in enumerate(probs)}
        })
    
    return predictions


# ========== 测试 ==========
if __name__ == "__main__":
    print("=" * 50)
    print("🧪 TF Serving REST API 测试")
    print("=" * 50)
    
    # 检查服务状态
    try:
        response = requests.get(f"{TF_SERVING_URL}")
        print(f"✅ TF Serving 运行中")
        print(f"   模型状态：{response.json()}")
    except requests.ConnectionError:
        print("❌ 无法连接 TF Serving")
        print("请确保已启动 TF Serving Docker 容器：")
        print("  docker run -d -p 8501:8501 ...")
        exit(1)
    
    # 单条预测
    print("\n📌 单条预测")
    result = predict([5.1, 3.5, 1.4, 0.2])
    print(f"   结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 批量预测
    print("\n📌 批量预测")
    samples = [
        [5.1, 3.5, 1.4, 0.2],
        [6.7, 3.0, 5.2, 2.3],
        [5.9, 3.0, 4.2, 1.5]
    ]
    results = predict_batch(samples)
    for i, r in enumerate(results):
        print(f"   样本{i+1}：{r['prediction']} ({max(r['probabilities'].values()):.2%})")
    
    print("\n✅ 测试完成！")
