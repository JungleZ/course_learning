# Day 4：FastAPI 部署模型

## 🎯 今日目标
1. 理解 FastAPI 与 Flask 的区别
2. 用 FastAPI 部署模型（自动生成 API 文档！）
3. 学习数据验证和类型提示

---

## 🆚 FastAPI vs Flask

| 特性 | Flask | FastAPI |
|------|-------|---------|
| 性能 | 较慢 | 非常快（异步） |
| 自动文档 | ❌ 需要手动写 | ✅ 自动生成 Swagger UI |
| 数据验证 | 手动检查 | Pydantic 自动验证 |
| 类型提示 | 不支持 | 原生支持 |
| 异步支持 | 需要扩展 | 原生支持 |
| 适合场景 | 简单应用 | 生产级 API |

**FastAPI 是目前 Python API 开发的最佳选择！**

---

## 📁 项目结构

```
day04-fastapi/
├── guide.md           # 本文件
├── main.py            # FastAPI 应用
├── test_api.py        # API 测试脚本
└── model/
    └── iris_model.pkl # 模型文件（运行 main.py 自动生成）
```

---

## 🚀 运行步骤

### 第1步：安装依赖
```bash
pip install fastapi uvicorn pydantic
```

### 第2步：启动 FastAPI 服务
```bash
cd day04-fastapi
python main.py
```

或者用 uvicorn 命令：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 第3步：查看自动生成的 API 文档
浏览器打开：http://127.0.0.1:8000/docs

**这是 FastAPI 最大的优势——自动生成交互式 API 文档！**
你可以在文档页面直接测试 API，不需要 Postman！

### 第4步：测试 API
```bash
# 健康检查
curl http://127.0.0.1:8000/health

# 预测
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d "{\"features\": [5.1, 3.5, 1.4, 0.2]}"

# 批量预测
curl -X POST http://127.0.0.1:8000/predict_batch \
  -H "Content-Type: application/json" \
  -d "{\"samples\": [[5.1, 3.5, 1.4, 0.2], [6.7, 3.0, 5.2, 2.3]]}"
```

---

## 🔑 关键概念

### Pydantic 数据验证
```python
from pydantic import BaseModel

class PredictRequest(BaseModel):
    features: list[float]  # 自动验证：必须是 float 列表
    
# 如果传了字符串，自动返回清晰的错误信息！
```

### 异步支持
```python
@app.post("/predict")
async def predict(request: PredictRequest):  # async = 异步
    # 可以同时处理多个请求，更快！
    pass
```

### 自动文档
- `/docs` - Swagger UI（交互式文档）
- `/redoc` - ReDoc（阅读友好文档）

---

## ✅ 今日检查清单
- [ ] 成功启动 FastAPI 服务
- [ ] 在 /docs 页面看到自动生成的 API 文档
- [ ] 通过 API 文档页面测试预测接口
- [ ] 理解 Pydantic 数据验证的作用
- [ ] 了解 FastAPI 相比 Flask 的优势

## 🎉 完成 Day 4！明天学习 Streamlit 可视化部署。
