# Day 10：HuggingFace Spaces 部署

## 🎯 今日目标
1. 了解 HuggingFace 平台
2. 部署 Transformer 模型到 HuggingFace Spaces
3. 学习使用 HuggingFace Transformers 库
4. 部署文本分类和图像分类 Demo

---

## 🤗 什么是 HuggingFace？

HuggingFace = AI 模型的 GitHub

| 功能 | 说明 |
|------|------|
| Model Hub | 30万+ 预训练模型 |
| Datasets | 海量数据集 |
| Spaces | 免费托管 ML Demo |
| Transformers | 最流行的 NLP 库 |

---

## 📁 项目结构

```
day10-huggingface/
├── guide.md         # 本文件
├── app.py           # Gradio 应用（文本分类）
└── requirements.txt # 依赖
```

---

## 🚀 运行步骤

### 第1步：安装依赖
```bash
pip install transformers gradio torch
```

### 第2步：本地运行
```bash
cd day10-huggingface
python app.py
```

### 第3步：部署到 HuggingFace Spaces

#### 3.1 创建 Space
1. 登录 https://huggingface.co
2. 点击 "New Space"
3. 填写信息：
   - **Space name**：你的应用名称
   - **SDK**：选择 **Gradio**
   - **Hardware**：Free CPU（免费）
4. 点击 "Create Space"

#### 3.2 上传代码

**方式1：Git 推送（推荐）**
```bash
# 克隆你的 Space
git clone https://huggingface.co/spaces/你的用户名/你的space名
cd 你的space名

# 复制文件
cp day10-huggingface/app.py .
cp day10-huggingface/requirements.txt .

# 推送
git add .
git commit -m "Add ML app"
git push
```

**方式2：网页上传**
在 Space 页面点击 "Files"，直接上传文件。

#### 3.3 等待构建
- 提交后自动构建，约1-3分钟
- 构建成功后就可以通过公网访问了！
- 地址：`https://huggingface.co/spaces/你的用户名/你的space名`

---

## 🔑 关键概念

### HuggingFace Transformers
```python
from transformers import pipeline

# 一行代码加载预训练模型
classifier = pipeline("text-classification")

# 一行代码做预测
result = classifier("I love this movie!")
# → [{'label': 'POSITIVE', 'score': 0.999}]
```

### Pipeline 类型

| Pipeline | 任务 | 示例 |
|----------|------|------|
| `text-classification` | 文本分类 | 情感分析 |
| `token-classification` | 序列标注 | 命名实体识别 |
| `question-answering` | 问答 | 阅读理解 |
| `summarization` | 摘要 | 文本摘要 |
| `translation` | 翻译 | 中英翻译 |
| `image-classification` | 图像分类 | 物体识别 |
| `automatic-speech-recognition` | 语音识别 | 语音转文字 |

---

## 📊 部署架构

```
┌─────────────────────────────────────┐
│      HuggingFace Spaces             │
│                                     │
│  ┌───────────┐    ┌──────────────┐ │
│  │  Gradio   │    │  Transformer │ │
│  │  界面     │ →  │  模型        │ │
│  │           │    │  (自动下载)   │ │
│  └───────────┘    └──────────────┘ │
│                                     │
│  自动构建 ← Git Push               │
│  免费托管 ← CPU 实例               │
└─────────────────────────────────────┘
          ↕ 公网访问
    https://huggingface.co/spaces/xxx
```

---

## 💡 高级技巧

### 指定特定模型
```python
# 默认用英文模型
classifier = pipeline("text-classification")

# 指定中文情感分析模型
classifier = pipeline("text-classification", model="uer/roberta-base-finetuned-jd-binary-chinese")
```

### 缓存模型（避免重复下载）
```python
import os
os.environ["TRANSFORMERS_CACHE"] = "./model_cache"
```

### 使用 GPU（Spaces 付费）
在 Space 设置中选择 GPU 硬件，推理速度大幅提升。

---

## ✅ 今日检查清单
- [ ] 成功安装 transformers 和 gradio
- [ ] 本地运行文本分类 Demo
- [ ] 注册 HuggingFace 账号
- [ ] 成功部署到 HuggingFace Spaces
- [ ] 通过公网 URL 访问你的应用
- [ ] 了解 pipeline 的不同类型

## 🎉 完成 Day 10！明天学习 TensorFlow Serving。
