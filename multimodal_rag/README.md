# 多模态视觉RAG系统
# 完全免费方案：像素特征 + FAISS + GPT-4o (可选API)

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 添加图片到 images/ 目录

# 3. 构建索引
cd src
python data_processing.py

# 4. 启动应用
python app.py
# 浏览器打开 http://127.0.0.1:7861
```

## 架构

```
[用户输入] → [编码器] → [FAISS检索] → [Top-K图片] → [GPT-4o/回答生成]
    文本/图片          CLIP/像素          向量搜索         多模态分析
```

## 配置API Key (可选)

```bash
# 启用GPT-4o生成回答
set OPENAI_API_KEY=your-key
```

## 项目结构

```
multimodal_rag/
├── images/                # 存放图片
├── index/                 # FAISS索引
│   ├── faiss_index.bin
│   ├── image_features.pkl
│   └── image_metadata.json
├── src/
│   ├── app.py             # Gradio界面
│   ├── image_encoder.py   # 图片编码器
│   ├── retriever.py       # FAISS检索器
│   ├── generator.py       # 回答生成器
│   └── data_processing.py # 图片索引构建
├── requirements.txt
└── README.md
```