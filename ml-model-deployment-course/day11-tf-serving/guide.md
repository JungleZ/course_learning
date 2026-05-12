# Day 11：TensorFlow Serving 部署

## 🎯 今日目标
1. 理解 TensorFlow Serving 的作用
2. 将 Keras 模型转换为 SavedModel 格式
3. 用 Docker 运行 TF Serving
4. 通过 gRPC 和 REST API 调用模型

---

## 🤔 什么是 TensorFlow Serving？

TF Serving = Google 开源的高性能模型服务系统

| 特性 | 说明 |
|------|------|
| 生产级 | 专为生产环境设计 |
| 高性能 | 支持批量推理、多线程 |
| 热更新 | 不停机更新模型 |
| 多模型 | 同时服务多个模型 |
| 版本管理 | 自动管理模型版本 |

### 与 Flask/FastAPI 的区别

| 对比 | Flask/FastAPI | TF Serving |
|------|---------------|------------|
| 定位 | 通用 Web 框架 | 专用模型服务 |
| 性能 | 一般 | **非常高** |
| 模型格式 | 任意 | SavedModel |
| 批量推理 | 手动实现 | **内置支持** |
| 热更新 | 手动实现 | **内置支持** |
| 适用 | 小规模 | **大规模生产** |

---

## 📁 项目结构

```
day11-tf-serving/
├── guide.md               # 本文件
├── train_and_export.py    # 训练模型并导出 SavedModel
├── Dockerfile             # TF Serving Docker 配置
├── client_rest.py         # REST API 客户端
└── client_grpc.py         # gRPC 客户端
```

---

## 🚀 运行步骤

### 第1步：安装 TensorFlow
```bash
pip install tensorflow requests grpcio
```

### 第2步：训练并导出模型
```bash
cd day11-tf-serving
python train_and_export.py
```

这会生成 `saved_model/iris_model/1/` 目录。

### 第3步：用 Docker 运行 TF Serving
```bash
docker run -d --name tf-serving \
    -p 8501:8501 \
    -p 8500:8500 \
    -v $(pwd)/saved_model:/models/iris_model \
    -e MODEL_NAME=iris_model \
    tensorflow/serving
```

参数说明：
- `-p 8501:8501`：REST API 端口
- `-p 8500:8500`：gRPC 端口
- `-v`：挂载模型目录
- `MODEL_NAME`：模型名称

### 第4步：测试 API

#### REST API
```bash
# 模型状态
curl http://localhost:8501/v1/models/iris_model

# 预测
curl -X POST http://localhost:8501/v1/models/iris_model:predict \
    -H "Content-Type: application/json" \
    -d '{"instances": [[5.1, 3.5, 1.4, 0.2]]}'
```

#### 用 Python 客户端
```bash
python client_rest.py
python client_grpc.py
```

---

## 🔑 关键概念

### SavedModel 格式
```
saved_model/
└── iris_model/
    └── 1/                    # 版本号
        ├── saved_model.pb    # 模型结构和权重
        └── variables/        # 变量文件
            ├── variables.index
            └── variables.data-00000-of-00001
```

### TF Serving API 端点

| 端点 | 方法 | 作用 |
|------|------|------|
| `/v1/models/{model}` | GET | 模型状态 |
| `/v1/models/{model}:predict` | POST | 预测 |
| `/v1/models/{model}:classify` | POST | 分类 |
| `/v1/models/{model}:regress` | POST | 回归 |

### 模型版本管理
```
saved_model/
└── iris_model/
    ├── 1/    # 版本1
    ├── 2/    # 版本2（自动使用最新版本）
    └── 3/    # 版本3
```
TF Serving 自动加载最新版本，实现**不停机更新**！

---

## 📊 部署架构

```
┌──────────────┐    REST/gRPC    ┌──────────────────┐
│   客户端      │ ──────────────→ │  TF Serving       │
│  (Python/    │                 │  (Docker 容器)     │
│   Java/Go/   │ ←────────────── │                   │
│   等)        │   预测结果       │  自动加载模型      │
└──────────────┘                 │  版本管理          │
                                  └────────┬─────────┘
                                           │
                                   ┌───────┴───────┐
                                   │  SavedModel    │
                                   │  v1, v2, v3... │
                                   └───────────────┘
```

---

## ⚠️ Windows 注意事项

TF Serving 官方只提供 Linux Docker 镜像。Windows 用户：
1. 使用 Docker Desktop + WSL2
2. 或在云服务器上运行

---

## ✅ 今日检查清单
- [ ] 成功安装 TensorFlow
- [ ] 训练模型并导出 SavedModel 格式
- [ ] 用 Docker 运行 TF Serving
- [ ] 通过 REST API 调用模型预测
- [ ] 了解 TF Serving 的优势和适用场景

## 🎉 完成 Day 11！明天学习 ONNX 模型优化。
