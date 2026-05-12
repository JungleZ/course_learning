"""
检索器模块
基于 FAISS + TF-IDF 的语义检索
纯 Python 实现，不依赖 langchain
"""
import os
import json
import pickle
import faiss
from typing import List, Tuple, Dict, Any, Optional


class Document:
    """模拟 LangChain Document 对象"""
    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        src = self.metadata.get('source', '未知')
        content = self.page_content[:60]
        return f"Document(source={src}, content={content}...)"


def _load_database(persist_dir: str = "./chroma_db"):
    """加载索引、向量化器、文本和元数据"""
    index = faiss.read_index(os.path.join(persist_dir, "faiss_index.bin"))
    with open(os.path.join(persist_dir, "tfidf_vectorizer.pkl"), 'rb') as f:
        vectorizer = pickle.load(f)
    with open(os.path.join(persist_dir, "doc_metadata.json"), 'r', encoding='utf-8') as f:
        metadatas = json.load(f)
    with open(os.path.join(persist_dir, "chunk_texts.json"), 'r', encoding='utf-8') as f:
        texts = json.load(f)
    return index, vectorizer, texts, metadatas


def create_retriever(persist_dir: str = "./chroma_db", k: int = 4) -> Dict:
    """
    创建检索器

    Returns:
        dict: 包含 index, vectorizer, texts, metadatas, k 的字典
    """
    index, vectorizer, texts, metadatas = _load_database(persist_dir)
    return {
        "index": index,
        "vectorizer": vectorizer,
        "texts": texts,
        "metadatas": metadatas,
        "k": k,
        "persist_dir": persist_dir
    }


def similarity_search(query: str, retriever: Dict, k: int = None) -> List[Document]:
    """
    执行相似度搜索

    Args:
        query: 用户查询
        retriever: 检索器字典
        k: 返回结果数量

    Returns:
        List[Document]: 检索到的文档列表
    """
    k = k or retriever["k"]
    k = min(k, retriever["index"].ntotal)

    index = retriever["index"]
    vectorizer = retriever["vectorizer"]
    texts = retriever["texts"]
    metadatas = retriever["metadatas"]

    # 查询向量化
    query_vec = vectorizer.transform([query]).toarray().astype('float32')
    faiss.normalize_L2(query_vec)

    # 搜索
    scores, indices = index.search(query_vec, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0 and idx < len(texts):
            doc = Document(
                page_content=texts[idx],
                metadata={**metadatas[idx], "score": float(score)}
            )
            results.append(doc)

    return results


def similarity_search_with_score(query: str, retriever: Dict, k: int = None) -> List[Tuple[Document, float]]:
    """
    带分数的相似度搜索

    Returns:
        List[Tuple[Document, float]]: (文档, 相关性分数) 列表
    """
    k = k or retriever["k"]
    results = similarity_search(query, retriever, k)
    return [(doc, doc.metadata.get("score", 0.0)) for doc in results]


def get_relevant_documents(query: str, persist_dir: str = "./chroma_db", k: int = 4) -> List[Document]:
    """
    获取与查询相关的文档（便捷函数）
    """
    retriever = create_retriever(persist_dir, k)
    return similarity_search(query, retriever, k)


def get_top_k_texts(query: str, persist_dir: str = "./chroma_db", k: int = 4) -> List[Tuple[str, str, float]]:
    """
    获取 top-k 相关文本（带分数）

    Returns:
        List[Tuple[source, content, score]]
    """
    retriever = create_retriever(persist_dir, k)
    results = similarity_search_with_score(query, retriever, k)
    return [
        (doc.metadata.get('source', '未知'), doc.page_content, score)
        for doc, score in results
    ]


def is_off_topic(query: str) -> bool:
    """
    判断用户问题是否偏离企业知识库范围

    Args:
        query: 用户输入的问题

    Returns:
        bool: 是否为离题问题
    """
    off_topic_keywords = [
        "天气", "下雨", "气温", "温度", "新闻", "娱乐", "明星", "电影",
        "今天几号", "现在几点", "几点了", "日期", "几点",
        "笑话", "故事", "诗歌", "帮我写", "翻译", "英语",
        "吃什么", "外卖", "点餐", "股票", "彩票",
        "你是谁", "你叫什么", "介绍一下你自己",
    ]
    query_lower = query.lower()
    for keyword in off_topic_keywords:
        if keyword in query_lower:
            return True
    return False


if __name__ == "__main__":
    # 直接运行时的测试
    db_path = "./chroma_db"
    if os.path.exists(os.path.join(db_path, "faiss_index.bin")):
        retriever = create_retriever(db_path)
        results = similarity_search("年度调薪的流程", retriever)
        print("检索到 %d 个结果:" % len(results))
        for doc in results:
            print("  [%s] 分数: %.4f" % (doc.metadata.get('source'), doc.metadata.get('score', 0)))
            print("  内容: %s..." % doc.page_content[:150])
            print()
    else:
        print("请先运行 data_processing.py 来构建向量索引")