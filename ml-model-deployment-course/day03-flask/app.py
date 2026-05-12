"""
Day 3: Flask API 部署机器学习模型

功能：
1. 加载训练好的模型
2. 提供 REST API 接口做预测
3. 提供简单的网页界面

运行方式：
1. 先运行 train_and_save.py 生成模型文件
2. 再运行本文件启动服务
3. 浏览器访问 http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import os

# ========== 创建 Flask 应用 ==========
app = Flask(__name__)

# ========== 加载模型 ==========
MODEL_PATH = "iris_model.pkl"

if not os.path.exists(MODEL_PATH):
    print("❌ 模型文件不存在！请先运行 train_and_save.py")
    print("   命令：python train_and_save.py")
    exit(1)

model = joblib.load(MODEL_PATH)
print(f"✅ 模型已从 {MODEL_PATH} 加载")

# 类别名称映射
CLASS_NAMES = ["山鸢尾 (setosa)", "变色鸢尾 (versicolor)", "维吉尼亚鸢尾 (virginica)"]


# ========== 定义路由 ==========

@app.route("/")
def home():
    """首页 - 提供网页界面"""
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    预测接口
    
    请求格式（JSON）：
    {
        "features": [5.1, 3.5, 1.4, 0.2]
    }
    
    响应格式（JSON）：
    {
        "prediction": "山鸢尾 (setosa)",
        "class_id": 0,
        "probabilities": [0.9, 0.05, 0.05]
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 检查数据格式
        if "features" not in data:
            return jsonify({"error": "请提供 features 字段"}), 400
        
        features = data["features"]
        
        # 检查特征数量
        if len(features) != 4:
            return jsonify({"error": "需要4个特征值（花萼长/宽，花瓣长/宽）"}), 400
        
        # 转换为 numpy 数组
        features_array = np.array([features], dtype=float)
        
        # 做预测
        prediction = model.predict(features_array)[0]
        
        # 获取预测概率（如果模型支持）
        try:
            probabilities = model.predict_proba(features_array)[0]
            prob_list = [round(float(p), 4) for p in probabilities]
        except AttributeError:
            prob_list = None
        
        # 构建响应
        result = {
            "prediction": CLASS_NAMES[prediction],
            "class_id": int(prediction),
            "input_features": features
        }
        if prob_list:
            result["probabilities"] = prob_list
        
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({"error": f"特征值必须是数字：{str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"预测出错：{str(e)}"}), 500


@app.route("/predict_form", methods=["POST"])
def predict_form():
    """处理网页表单提交的预测请求"""
    try:
        # 从表单获取数据
        sepal_length = float(request.form.get("sepal_length", 0))
        sepal_width = float(request.form.get("sepal_width", 0))
        petal_length = float(request.form.get("petal_length", 0))
        petal_width = float(request.form.get("petal_width", 0))
        
        features = [sepal_length, sepal_width, petal_length, petal_width]
        features_array = np.array([features])
        
        prediction = model.predict(features_array)[0]
        
        try:
            probabilities = model.predict_proba(features_array)[0]
            prob_list = [round(float(p), 4) for p in probabilities]
        except AttributeError:
            prob_list = None
        
        return render_template("index.html",
            prediction=CLASS_NAMES[prediction],
            probabilities=prob_list,
            class_names=CLASS_NAMES,
            features=features
        )
    except Exception as e:
        return render_template("index.html", error=str(e))


@app.route("/health", methods=["GET"])
def health():
    """健康检查接口"""
    return jsonify({"status": "healthy", "model_loaded": True})


# ========== 启动服务 ==========
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🌸 鸢尾花分类 Flask API 服务")
    print("=" * 50)
    print("📖 API 文档：")
    print("   首页：http://127.0.0.1:5000/")
    print("   预测：POST http://127.0.0.1:5000/predict")
    print("   健康检查：GET http://127.0.0.1:5000/health")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
