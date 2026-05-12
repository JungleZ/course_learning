"""
Day 4: FastAPI 部署机器学习模型

功能：
1. 自动训练并保存模型（首次运行）
2. 提供 REST API 接口做预测
3. 自动生成 API 文档（Swagger UI）
4. 数据验证（Pydantic）
5. 批量预测支持

运行方式：
    python main.py
    或者：uvicorn main:app --reload --host 0.0.0.0 --port 8000

API 文档：http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import joblib
import numpy as np
import os
from typing import List

# ========== 数据模型（Pydantic 自动验证） ==========

class PredictRequest(BaseModel):
    """单条预测请求"""
    features: List[float] = Field(
        ...,  # 必填字段
        min_length=4,
        max_length=4,
        description="4个特征值：花萼长度、花萼宽度、花瓣长度、花瓣宽度"
    )

class PredictResponse(BaseModel):
    """单条预测响应"""
    prediction: str = Field(description="预测的鸢尾花品种")
    class_id: int = Field(description="类别编号")
    confidence: float = Field(description="最高概率")
    probabilities: List[float] = Field(description="各类别概率")

class BatchPredictRequest(BaseModel):
    """批量预测请求"""
    samples: List[List[float]] = Field(
        ...,
        description="多个样本的特征列表，每个样本4个特征"
    )

class BatchPredictResponse(BaseModel):
    """批量预测响应"""
    predictions: List[PredictResponse]
    count: int

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    model_loaded: bool
    model_accuracy: float


# ========== 创建 FastAPI 应用 ==========
app = FastAPI(
    title="🌸 鸢尾花分类 API",
    description="基于机器学习的鸢尾花品种预测服务，使用 FastAPI 构建",
    version="1.0.0"
)

# ========== 类别名称 ==========
CLASS_NAMES = ["山鸢尾 (setosa)", "变色鸢尾 (versicolor)", "维吉尼亚鸢尾 (virginica)"]

# ========== 模型管理 ==========
MODEL_PATH = os.path.join(os.path.dirname(__file__), "iris_model.pkl")
model = None
model_accuracy = 0.0


def train_and_save_model():
    """训练并保存模型"""
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.metrics import accuracy_score

    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )

    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(X_train, y_train)

    global model_accuracy
    model_accuracy = accuracy_score(y_test, clf.predict(X_test))

    joblib.dump(clf, MODEL_PATH)
    print(f"✅ 模型训练完成，准确率：{model_accuracy:.2%}")
    return clf


def load_model():
    """加载模型"""
    global model, model_accuracy
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"✅ 模型已从 {MODEL_PATH} 加载")
    else:
        print("⚠️ 模型文件不存在，开始训练...")
        model = train_and_save_model()


# ========== 启动时加载模型 ==========
@app.on_event("startup")
async def startup():
    load_model()


# ========== API 路由 ==========

@app.get("/", response_class=HTMLResponse)
async def home():
    """首页"""
    return """
    <html>
    <head><title>🌸 鸢尾花分类 API</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🌸 鸢尾花分类 API</h1>
        <p>基于 FastAPI 构建的机器学习模型部署服务</p>
        <br>
        <a href="/docs" style="font-size: 20px;">📖 打开 API 文档（Swagger UI）</a>
        <br><br>
        <a href="/redoc" style="font-size: 20px;">📖 打开 API 文档（ReDoc）</a>
    </body>
    </html>
    """


@app.get("/health", response_model=HealthResponse)
async def health():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        model_accuracy=model_accuracy
    )


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    预测鸢尾花品种
    
    输入4个特征值，返回预测的品种和概率。
    
    - **features**: [花萼长度, 花萼宽度, 花瓣长度, 花瓣宽度]
    """
    if model is None:
        raise HTTPException(status_code=503, detail="模型未加载")
    
    try:
        features_array = np.array([request.features])
        prediction = model.predict(features_array)[0]
        probabilities = model.predict_proba(features_array)[0]
        
        return PredictResponse(
            prediction=CLASS_NAMES[prediction],
            class_id=int(prediction),
            confidence=float(probabilities[prediction]),
            probabilities=[round(float(p), 4) for p in probabilities]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测出错：{str(e)}")


@app.post("/predict_batch", response_model=BatchPredictResponse)
async def predict_batch(request: BatchPredictRequest):
    """
    批量预测鸢尾花品种
    
    一次提交多个样本的特征，批量获取预测结果。
    """
    if model is None:
        raise HTTPException(status_code=503, detail="模型未加载")
    
    results = []
    for i, sample in enumerate(request.samples):
        if len(sample) != 4:
            raise HTTPException(
                status_code=400,
                detail=f"第 {i+1} 个样本需要4个特征值，当前有 {len(sample)} 个"
            )
        
        features_array = np.array([sample])
        prediction = model.predict(features_array)[0]
        probabilities = model.predict_proba(features_array)[0]
        
        results.append(PredictResponse(
            prediction=CLASS_NAMES[prediction],
            class_id=int(prediction),
            confidence=float(probabilities[prediction]),
            probabilities=[round(float(p), 4) for p in probabilities]
        ))
    
    return BatchPredictResponse(predictions=results, count=len(results))


@app.post("/retrain")
async def retrain():
    """重新训练模型"""
    global model
    model = train_and_save_model()
    return {"message": "模型重新训练完成", "accuracy": f"{model_accuracy:.2%}"}


# ========== 启动服务 ==========
if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 50)
    print("🌸 鸢尾花分类 FastAPI 服务")
    print("=" * 50)
    print("📖 API 文档：http://127.0.0.1:8000/docs")
    print("📖 ReDoc 文档：http://127.0.0.1:8000/redoc")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
