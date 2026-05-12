# Day 3：Flask API 部署模型

## 🎯 今日目标
1. 理解什么是 API 服务
2. 用 Flask 把模型包装成 REST API
3. 通过 HTTP 请求调用模型做预测

---

## 🤔 什么是 API 部署？

把模型变成一个**服务**，别人通过网络请求就能使用你的模型：

```
用户 → HTTP请求 → Flask服务 → 模型预测 → 返回结果
```

就像你在餐厅点菜：
- 你（客户端）告诉服务员（API）你要什么
- 服务员告诉厨房（模型）去做
- 厨房做好后，服务员把菜端给你（返回预测结果）

---

## 📁 项目结构

```
day03-flask/
├── guide.md           # 本文件
├── app.py             # Flask 应用主文件
├── train_and_save.py  # 训练并保存模型
└── templates/
    └── index.html     # 网页界面
```

---

## 🚀 运行步骤

### 第1步：训练并保存模型

```bash
cd day03-flask
python train_and_save.py
```

这会生成 `iris_model.pkl` 文件。

### 第2步：启动 Flask 服务

```bash
python app.py
```

你会看到：
```
 * Running on http://127.0.0.1:5000
```

### 第3步：测试 API

#### 方式1：浏览器打开
访问 http://127.0.0.1:5000 ，在网页上输入数据预测

#### 方式2：用 curl 命令
```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d "{\"features\": [5.1, 3.5, 1.4, 0.2]}"
```

#### 方式3：用 Python requests
```python
import requests
response = requests.post(
    "http://127.0.0.1:5000/predict",
    json={"features": [5.1, 3.5, 1.4, 0.2]}
)
print(response.json())
```

---

## 🔑 关键概念

### REST API
- **R**epresentational **S**tate **T**ransfer
- 一种设计风格，用 HTTP 方法操作资源
- GET = 获取信息，POST = 提交数据

### Flask 路由
```python
@app.route('/predict', methods=['POST'])  # 定义URL和HTTP方法
def predict():
    # 处理请求，返回预测结果
    pass
```

### JSON 格式
- API 最常用的数据交换格式
- 请求：`{"features": [5.1, 3.5, 1.4, 0.2]}`
- 响应：`{"prediction": "setosa", "confidence": 0.95}`

---

## 📊 部署架构

```
┌──────────┐     HTTP POST      ┌──────────────┐
│  客户端   │ ──────────────────→ │  Flask 服务器  │
│(浏览器/   │   JSON 请求数据     │  (app.py)     │
│ Python/   │                    │               │
│ curl)     │ ←────────────────── │  加载模型      │
│           │   JSON 预测结果     │  做预测        │
└──────────┘                     └──────────────┘
                                        │
                                 ┌──────┴──────┐
                                 │ model.pkl   │
                                 │ (保存的模型)  │
                                 └─────────────┘
```

---

## ⚠️ Flask 生产部署注意

Flask 自带的开发服务器**不适合生产环境**！生产环境需要：

| 工具 | 作用 |
|------|------|
| gunicorn | Linux 上的 WSGI 服务器 |
| waitress | Windows 上的 WSGI 服务器 |
| nginx | 反向代理，处理静态文件 |

生产部署命令：
```bash
# Linux
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Windows
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

---

## 🐛 常见问题

### Q: 启动后访问不了
A: 检查是否在正确的目录下，确保 `model.pkl` 文件存在

### Q: 提示 "ModuleNotFoundError: No module named 'flask'"
A: 运行 `pip install flask`

### Q: POST 请求返回 400 错误
A: 检查 JSON 格式是否正确，features 数组需要有 4 个数值

---

## ✅ 今日检查清单
- [ ] 理解 API 部署的概念
- [ ] 成功运行 train_and_save.py 生成模型文件
- [ ] 成功启动 Flask 服务
- [ ] 通过浏览器或 curl 调用 API 获得预测结果
- [ ] 理解 REST API 的工作流程

## 🎉 完成 Day 3！明天学习更现代的 FastAPI 部署方式。
