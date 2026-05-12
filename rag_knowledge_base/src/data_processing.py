"""
数据预处理与建库模块
纯 Python 实现：文档加载、切分、TF-IDF 向量化、FAISS 索引
无需 langchain 依赖
"""
import os
import re
import json
import pickle
import numpy as np
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer


# ============ 配置 ============
INDEX_FILE = "faiss_index.bin"
VECTORIZER_FILE = "tfidf_vectorizer.pkl"
METADATA_FILE = "doc_metadata.json"
TEXTS_FILE = "chunk_texts.json"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _read_markdown(filepath: str) -> str:
    """读取 Markdown 文件内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def _read_txt(filepath: str) -> str:
    """读取 TXT 文件内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def _read_docx(filepath: str) -> str:
    """读取 Word 文档内容"""
    try:
        from docx import Document as DocxDocument
        doc = DocxDocument(filepath)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except ImportError:
        print(f"  ⚠️ python-docx 未安装，跳过 Word 文件: {filepath}")
        return ""


def _read_pdf(filepath: str) -> str:
    """读取 PDF 文件内容"""
    try:
        from pdfminer.high_level import extract_text
        return extract_text(filepath)
    except ImportError:
        print(f"  ⚠️ pdfminer 未安装，跳过 PDF 文件: {filepath}")
        return ""


def _load_file(filepath: str) -> str:
    """根据文件扩展名加载文档"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.md':
        return _read_markdown(filepath)
    elif ext == '.txt':
        return _read_txt(filepath)
    elif ext == '.docx':
        return _read_docx(filepath)
    elif ext == '.pdf':
        return _read_pdf(filepath)
    else:
        print(f"  ⚠️ 不支持的文件格式: {ext}")
        return ""


def _split_text(text: str, chunk_size: int = CHUNK_SIZE,
                overlap: int = CHUNK_OVERLAP) -> list:
    """
    按语义边界切分文本
    优先按标题、空行、句子结束切分
    """
    # 按标题和空行分割大块
    blocks = re.split(r'\n\s*\n', text)

    chunks = []
    current_chunk = ""

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # 如果当前块加上新块不超过大小限制，合并
        if len(current_chunk) + len(block) + 2 <= chunk_size:
            if current_chunk:
                current_chunk += "\n\n" + block
            else:
                current_chunk = block
        else:
            # 当前块满了，保存
            if current_chunk:
                chunks.append(current_chunk)

            # 如果单个 block 就超过 chunk_size，按句子切分
            if len(block) > chunk_size:
                sentences = re.split(r'(。|！|？|\n)', block)
                temp = ""
                for sent in sentences:
                    if len(temp) + len(sent) <= chunk_size:
                        temp += sent
                    else:
                        if temp:
                            chunks.append(temp.strip())
                        temp = sent
                if temp.strip():
                    chunks.append(temp.strip())
            else:
                current_chunk = block

    # 保存最后一个块
    if current_chunk:
        chunks.append(current_chunk)

    # 应用 overlap：在相邻块之间添加重叠文本
    if overlap > 0 and len(chunks) > 1:
        overlapped_chunks = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                # 从上一个块末尾取 overlap 长度的文本作为前缀
                prev_chunk = chunks[i - 1]
                words = prev_chunk.split()
                overlap_text = " ".join(words[-overlap // 5:]) if len(words) > overlap // 5 else prev_chunk[-(overlap // 2):]
                chunk = overlap_text + "\n" + chunk
            overlapped_chunks.append(chunk)
        return overlapped_chunks

    return chunks


def _get_doc_files(doc_dir: str) -> list:
    """获取目录下的所有支持文件"""
    supported_exts = ['.md', '.txt', '.pdf', '.docx']
    files = []
    for root, _, filenames in os.walk(doc_dir):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in supported_exts:
                files.append(os.path.join(root, filename))
    return files


def process_documents(doc_dir: str = "./data", persist_dir: str = "./chroma_db"):
    """
    加载、切分文档，构建 TF-IDF 向量并存入 FAISS 索引

    Args:
        doc_dir: 存放原始文档的目录
        persist_dir: 向量索引持久化目录
    """
    print("[DB] 开始构建知识库...")
    print("=" * 50)

    os.makedirs(persist_dir, exist_ok=True)

    # 检查文档目录
    files = _get_doc_files(doc_dir)
    print(f"\n[FILES] 在 {doc_dir} 中找到 {len(files)} 个文档文件:")
    for f in files:
        print(f"   - {os.path.basename(f)}")

    if len(files) == 0:
        print("\n[WARN] 文档目录中没有找到任何支持的文件")
        print("   请在 data/ 目录下添加 .md / .txt / .pdf / .docx 文件")
        return None

    # 1. 加载文档
    print("\n[LOAD] 正在加载文档...")
    documents = {}  # filepath -> content
    for filepath in files:
        content = _load_file(filepath)
        if content.strip():
            documents[filepath] = content
            print(f"   OK {os.path.basename(filepath)} ({len(content)} 字符)")
        else:
            print(f"   SKIP {os.path.basename(filepath)} (内容为空或读取失败)")

    print(f"\n[OK] 成功加载 {len(documents)} 个文档")

    # 2. 文档切分
    print("\n[SPLIT] 正在切分文档...")
    all_chunks = []
    all_metadatas = []

    for filepath, content in documents.items():
        chunks = _split_text(content)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "source": f"{os.path.basename(filepath)}",
                "filepath": filepath,
                "chunk_index": i,
                "chunk_size": len(chunk),
            })

    print(f"[OK] 切分为 {len(all_chunks)} 个文本块")

    # 3. TF-IDF 向量化
    print("\n[VECTORIZE] 正在构建 TF-IDF 向量模型...")
    vectorizer = TfidfVectorizer(
        max_features=50000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        norm='l2',
        min_df=1,
        max_df=0.95,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(all_chunks)
    except ValueError as e:
        # 如果只有一个文档且切分后只有一个块，可能出错
        print(f"⚠️ 向量化出错: {e}")
        if len(all_chunks) == 0:
            return None
        # 尝试退回到简单分词
        vectorizer = TfidfVectorizer(
            max_features=50000,
            ngram_range=(1, 1),
            sublinear_tf=True,
            norm='l2',
            token_pattern=r'(?u)\b\w+\b',
        )
        tfidf_matrix = vectorizer.fit_transform(all_chunks)

    print(f"[OK] TF-IDF 矩阵维度: {tfidf_matrix.shape}")

    # 4. 构建 FAISS 索引
    print("\n[INDEX] 正在构建 FAISS 索引...")
    dim = tfidf_matrix.shape[1]
    dense_matrix = tfidf_matrix.toarray().astype('float32')

    # L2 归一化（使内积等价于余弦相似度）
    faiss.normalize_L2(dense_matrix)

    index = faiss.IndexFlatIP(dim)  # 内积索引 = 余弦相似度
    index.add(dense_matrix)
    print(f"[OK] FAISS 索引已创建，共 {index.ntotal} 个向量，维度 {dim}")

    # 5. 持久化
    faiss.write_index(index, os.path.join(persist_dir, INDEX_FILE))
    with open(os.path.join(persist_dir, VECTORIZER_FILE), 'wb') as f:
        pickle.dump(vectorizer, f)
    with open(os.path.join(persist_dir, METADATA_FILE), 'w', encoding='utf-8') as f:
        json.dump(all_metadatas, f, ensure_ascii=False, indent=2)
    with open(os.path.join(persist_dir, TEXTS_FILE), 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 向量数据库已保存至: {persist_dir}")
    print(f"   - 索引文件: {INDEX_FILE}")
    print(f"[VEC] 向量化器: {VECTORIZER_FILE}")
    print(f"[META] 元数据:   {METADATA_FILE}")
    print(f"   - 文本:     {TEXTS_FILE}")
    print("=" * 50)
    return index, vectorizer, all_chunks, all_metadatas


def load_database(persist_dir: str = "./chroma_db"):
    """
    从磁盘加载已有的向量数据库

    Returns:
        (index, vectorizer, texts, metadatas)
    """
    index = faiss.read_index(os.path.join(persist_dir, INDEX_FILE))
    with open(os.path.join(persist_dir, VECTORIZER_FILE), 'rb') as f:
        vectorizer = pickle.load(f)
    with open(os.path.join(persist_dir, METADATA_FILE), 'r', encoding='utf-8') as f:
        metadatas = json.load(f)
    with open(os.path.join(persist_dir, TEXTS_FILE), 'r', encoding='utf-8') as f:
        texts = json.load(f)

    print(f"[OK] 向量数据库已从 {persist_dir} 加载")
    print(f"   索引包含 {index.ntotal} 个向量")
    return index, vectorizer, texts, metadatas


if __name__ == "__main__":
    # 根据脚本位置自动计算正确的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    doc_dir = os.path.join(project_dir, "data")
    persist_dir = os.path.join(script_dir, "chroma_db")
    process_documents(doc_dir, persist_dir)
    print("\n测试检索...")
    index, vectorizer, texts, metadatas = load_database(persist_dir)
    query = "年度调薪的流程"
    query_vec = vectorizer.transform([query]).toarray().astype('float32')
    faiss.normalize_L2(query_vec)
    scores, indices = index.search(query_vec, 4)
    print(f"查询: '{query}'")
    print(f"找到 {len(indices[0])} 个结果:")
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0:
            print(f"  [分数: {score:.4f}] {metadatas[idx]['source']} - {texts[idx][:80]}...")