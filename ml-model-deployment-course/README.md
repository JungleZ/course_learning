# 🚀 2周课程：机器学习/深度学习模型部署实战

> **从小白到上线！** 零基础学会在不同平台部署 ML/DL 模型

## 📋 课程概览

| 项目 | 详情 |
|------|------|
| 课程时长 | 2周（14天） |
| 适合人群 | 零基础小白、Python入门者、想上线模型的学习者 |
| 前置要求 | 会写基础 Python（变量、函数、if/for）即可 |
| 涉及平台 | 本地电脑 · 云服务器 · Docker · 云平台（Streamlit/Gradio/HuggingFace） · 移动端 |
| 配套代码 | 本仓库所有代码均可直接运行 |

---

## 🗓️ 课程日历

| 天数 | 主题 | 部署平台 | 难度 |
|------|------|----------|------|
| Day 1 | 环境搭建 + 训练第一个模型 | 本地 | ⭐ |
| Day 2 | 模型保存与加载 | 本地 | ⭐ |
| Day 3 | Flask API 部署模型 | 本地服务 | ⭐⭐ |
| Day 4 | FastAPI 部署模型 | 本地服务 | ⭐⭐ |
| Day 5 | Streamlit 可视化部署 | Streamlit Cloud | ⭐⭐ |
| Day 6 | Gradio 快速构建 Demo | HuggingFace Spaces | ⭐⭐ |
| Day 7 | 🏠 休息日 + 总结复习 | — | — |
| Day 8 | Docker 容器化部署 | Docker | ⭐⭐⭐ |
| Day 9 | 云服务器部署（阿里云/腾讯云） | Linux 云服务器 | ⭐⭐⭐ |
| Day 10 | HuggingFace Spaces 部署 | HuggingFace | ⭐⭐ |
| Day 11 | TensorFlow Serving 部署 | Docker + TF Serving | ⭐⭐⭐ |
| Day 12 | ONNX 模型优化与部署 | ONNX Runtime | ⭐⭐⭐ |
| Day 13 | 移动端部署入门 | Android/iOS 基础 | ⭐⭐⭐ |
| Day 14 | 🎓 毕业项目：完整部署流水线 | 全平台 | ⭐⭐⭐ |

---

## 📦 项目结构

```
ml-model-deployment-course/
├── README.md                    # 本文件（课程大纲）
├── day01-environment/           # Day 1 环境搭建
│   ├── guide.md
│   └── train_first_model.py
├── day02-save-load/             # Day 2 模型保存加载
│   ├── guide.md
│   └── save_load_model.py
├── day03-flask/                 # Day 3 Flask部署
│   ├── guide.md
│   ├── app.py
│   └── templates/
│       └── index.html
├── day04-fastapi/               # Day 4 FastAPI部署
│   ├── guide.md
│   ├── main.py
│   └── test_api.py
├── day05-streamlit/             # Day 5 Streamlit部署
│   ├── guide.md
│   └── app.py
├── day06-gradio/                # Day 6 Gradio部署
│   ├── guide.md
│   └── app.py
├── day08-docker/                # Day 8 Docker部署
│   ├── guide.md
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── day09-cloud-server/          # Day 9 云服务器部署
│   └── guide.md
├── day10-huggingface/           # Day 10 HuggingFace部署
│   ├── guide.md
│   └── app.py
├── day11-tf-serving/            # Day 11 TF Serving
│   ├── guide.md
│   └── Dockerfile
├── day12-onnx/                  # Day 12 ONNX部署
│   ├── guide.md
│   ├── convert_to_onnx.py
│   └── onnx_inference.py
├── day13-mobile/                # Day 13 移动端部署
│   └── guide.md
├── day14-final-project/         # Day 14 毕业项目
│   ├── guide.md
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
└── shared/                      # 共享模型文件
    └── train_model.py           # 统一训练脚本
```

---

## 🔧 第一周：基础部署篇

详见各 dayXX 目录下的 `guide.md`
