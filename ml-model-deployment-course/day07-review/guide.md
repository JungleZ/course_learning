# Day 7：🏠 休息日 + 第一周总结复习

## 🎯 今日目标
1. 复习第一周学到的知识
2. 对比不同部署方式
3. 为第二周的高级内容做准备

---

## 📝 第一周知识回顾

### 我们学了什么？

| 天数 | 主题 | 核心技能 |
|------|------|---------|
| Day 1 | 环境搭建 | Python + sklearn 安装、模型训练 |
| Day 2 | 模型保存与加载 | joblib/pickle/torch.save 不同格式 |
| Day 3 | Flask API 部署 | REST API、路由、HTTP 请求 |
| Day 4 | FastAPI 部署 | Pydantic 验证、自动文档、异步 |
| Day 5 | Streamlit 部署 | 纯 Python 写界面、实时交互 |
| Day 6 | Gradio 部署 | 快速 ML Demo、HuggingFace Spaces |

---

## 📊 部署方式对比

| 部署方式 | 难度 | 代码量 | 适合场景 | 部署平台 |
|----------|------|--------|---------|---------|
| Flask API | ⭐⭐ | 中等 | 需要 API 服务 | 云服务器 |
| FastAPI | ⭐⭐ | 中等 | 生产级 API 服务 | 云服务器 |
| Streamlit | ⭐ | 少 | 数据应用/仪表盘 | Streamlit Cloud |
| Gradio | ⭐ | 最少 | ML Demo 展示 | HuggingFace Spaces |

---

## 🔗 部署流程总结

```
训练模型 → 保存模型 → 选择部署方式 → 构建应用 → 部署上线

具体来说：
1. 训练：用 sklearn/PyTorch/TensorFlow 训练模型
2. 保存：joblib(.pkl) / torch.save(.pth) / SavedModel
3. 选择：
   - 内部使用 → Flask/FastAPI API
   - 展示 Demo → Gradio/Streamlit
   - 数据分析 → Streamlit
4. 构建：写接口/界面代码
5. 部署：云服务器 / 云平台
```

---

## 🏋️ 复习练习

### 练习1：用自己的数据训练模型
尝试用 sklearn 的其他数据集（如 `load_wine`、`load_breast_cancer`）训练一个分类模型。

### 练习2：用不同方式部署同一个模型
用 Flask 和 FastAPI 分别部署你的模型，对比开发体验。

### 练习3：部署到云平台
选择 Streamlit Cloud 或 HuggingFace Spaces，把你的应用部署上线。

---

## 📚 第二周预告

| 天数 | 主题 | 你将学到 |
|------|------|---------|
| Day 8 | Docker 容器化 | 把应用打包成容器，到处运行 |
| Day 9 | 云服务器部署 | 在阿里云/腾讯云部署模型 |
| Day 10 | HuggingFace 部署 | 部署 Transformer 模型 |
| Day 11 | TF Serving | 生产级模型服务 |
| Day 12 | ONNX 优化 | 跨平台模型优化 |
| Day 13 | 移动端部署 | 在手机上运行模型 |
| Day 14 | 毕业项目 | 完整部署流水线 |

---

## 💡 休息建议

- 😴 好好休息
- 🔄 回顾之前不熟悉的内容
- 💻 试试上面的练习题
- 📖 如果有余力，预习 Docker 基础概念

## 🎉 休息好，明天开始第二周的高级部署！
