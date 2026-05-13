"""
多模态视觉 RAG 系统
完全免费方案：CLIP (本地模型) + FAISS (本地向量库) + GPT-4o API (可选/可Mock)

项目结构:
    multimodal_rag/
    ├── images/                    # 存放待索引的图片
    ├── index/                     # FAISS索引 + 图片描述缓存
    ├── src/
    │   ├── __init__.py
    │   ├── image_encoder.py       # CLIP 图片/文本编码器
    │   ├── retriever.py           # FAISS 向量检索
    │   ├── generator.py           # LLM 多模态回答生成 (GPT-4o)
    │   ├── data_processing.py     # 批量图片索引
    │   └── app.py                 # Gradio 交互界面
    ├── requirements.txt
    └── README.md

依赖: Python 3.7+
"""