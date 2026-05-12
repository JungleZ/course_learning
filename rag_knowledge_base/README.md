# 企业智能知识库问答助手 RAG Toolkit

> 基于 TF-IDF + FAISS + OpenAI 兼容 LLM 的企业知识库问答系统

## 📁 项目结构

```
rag_knowledge_base/
├── data/                       # 存放原始文档（Markdown/Word/PDF/TXT）
│   ├── 员工手册.md
│   ├── 2024年调薪政策.md
│   ├── 产品FAQ.md
│   ├── 前端开发技术规范.md
│   └── 2024年项目总结.md
├── src/                        # 核心源代码
│   ├── __init__.py
│   ├── data_processing.py      # 文档加载、切分、TF-IDF向量化、FAISS索引
│   ├── retriever.py            # FAISS检索器，提供语义搜索能力
│   ├── generator.py            # LLM生成器，构造Prompt并调用API生成回答
│   └── app.py                  # Gradio Web应用，整合所有模块
├── chroma_db/                  # 向量数据库持久化目录（FAISS索引）
│   ├── faiss_index.bin
│   ├── tfidf_vectorizer.pkl
│   ├── doc_metadata.json
│   └── chunk_texts.json
├── requirements.txt            # Python依赖
└── README.md
```

## 🏗️ 技术架构

```
用户提问 → TF-IDF向量化 → FAISS向量检索 → Top-K相关文档
                                                    ↓
                              构建增强Prompt → LLM生成回答 → 返回用户+来源标注
```

**核心组件选择：**

| 组件 | 技术方案 | 说明 |
|------|---------|------|
| 文档加载 | 自定义解析器 | 支持 .md / .txt / .pdf / .docx |
| 文本切分 | 正则语义切分 | 按标题、空行、句子边界智能切分，支持overlap |
| 嵌入模型 | TF-IDF (scikit-learn) | 轻量高效，无需GPU，适合企业内部术语 |
| 向量数据库 | FAISS (CPU) | Facebook开源，亿级向量检索毫秒级响应 |
| LLM生成 | OpenAI兼容API | 支持Qwen-Plus/GPT-4o-mini等 |
| Web框架 | Gradio | 快速构建美观的交互界面 |

## 🚀 快速开始

### 1. 环境准备

```bash
# 确保 Python >= 3.7
python --version

# 安装依赖
pip install -r requirements.txt
```

### 2. 添加文档

将公司内部的 `.md` / `.txt` / `.pdf` / `.docx` 文档放入 `data/` 目录：

```
data/
├── 员工手册.md
├── 2024年调薪政策.md
├── 产品FAQ.md
└── ...
```

### 3. 初始化知识库

```bash
cd src
python data_processing.py
```

首次运行会自动：
- 加载所有文档
- 按语义边界智能切分
- 使用 TF-IDF 向量化
- 构建并保存 FAISS 索引

### 4. 启动问答助手

```bash
cd src
python app.py
```

然后在浏览器中打开 **http://127.0.0.1:7860**

## 💡 使用方式

### 配置 LLM API Key

**方式一：环境变量（推荐）**
```bash
# 阿里云通义千问
export DASHSCOPE_API_KEY='your-dashscope-api-key'

# 或 OpenAI
export OPENAI_API_KEY='your-openai-api-key'
```

**方式二：修改代码**
```python
generator = create_generator("qwen", api_key="your-key")
```

> ⚠️ 未配置 API Key 时，系统将以 Mock 模式运行，仅展示检索到的原文片段。

### 交互界面功能

- **智能问答**：输入自然语言问题，系统自动检索并生成带来源的回答
- **答案溯源**：每个回答下方显示引用的文档来源
- **领域限定**：自动拒绝天气、新闻等无关问题
- **知识库重建**：添加新文档后点击"重建知识库"按钮重新索引
- **对话历史**：支持多轮对话上下文

## 📋 核心功能清单

- [x] Markdown 文档支持
- [x] TXT 文本文件支持
- [x] Word 文档支持（需 python-docx）
- [x] PDF 文件支持（需 pdfminer.six）
- [x] 语义级文本切分（支持 overlap）
- [x] TF-IDF 向量化（支持 bigram）
- [x] FAISS 余弦相似度检索
- [x] OpenAI 兼容 API 回答生成
- [x] 答案来源标注与溯源
- [x] 离题问题自动过滤
- [x] Gradio 交互界面
- [x] 知识库重建功能
- [ ] PDF表格提取优化
- [ ] 混合检索（BM25+向量）
- [ ] 重排序模型
- [ ] 用户反馈与日志分析

## 🔧 后续优化方向

1. **混合检索**：结合关键词搜索（BM25）和向量搜索，应对精确匹配需求
2. **重排序（Rerank）**：检索后加入交叉编码器精排
3. **更好的切分策略**：根据文档结构（标题、段落）语义切分
4. **Prompt 工程**：使用 CO-STAR 等框架优化提示词
5. **多模态支持**：支持图片、表格内容提取
6. **持久化记忆**：保存问答历史，支持多用户会话