"""
多模态检索器
基于FAISS的视觉特征向量检索
"""
import os
import json
import pickle
import numpy as np
import faiss
from typing import List, Dict


class VisualRetriever:
    """
    视觉检索器
    使用FAISS进行高效的近似最近邻搜索
    """

    def __init__(self, persist_dir: str = "./index", dim: int = 128):
        self.persist_dir = persist_dir
        self.dim = dim
        self.index = None
        self.metadatas = []
        self.features = None

    def build_index(self, features: np.ndarray, metadatas: list):
        """从特征和元数据构建索引"""
        self.features = features.astype(np.float32)
        faiss.normalize_L2(self.features)
        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(self.features)
        self.metadatas = metadatas
        print("[INDEX] 构建完成: %d 个向量, 维度 %d" % (self.index.ntotal, self.dim))

    def load(self, persist_dir: str = None) -> bool:
        """从磁盘加载索引"""
        if persist_dir:
            self.persist_dir = persist_dir

        idx_path = os.path.join(self.persist_dir, "faiss_index.bin")
        meta_path = os.path.join(self.persist_dir, "image_metadata.json")
        feat_path = os.path.join(self.persist_dir, "image_features.pkl")

        if not os.path.exists(idx_path):
            print("[WARN] 索引文件不存在: %s" % idx_path)
            return False

        self.index = faiss.read_index(idx_path)
        with open(meta_path, 'r', encoding='utf-8') as f:
            self.metadatas = json.load(f)
        with open(feat_path, 'rb') as f:
            self.features = pickle.load(f)

        print("[RETRIEVER] 已加载: %d 张图片, 维度 %d" % (self.index.ntotal, self.dim))
        return True

    def save(self):
        """保存索引到磁盘"""
        os.makedirs(self.persist_dir, exist_ok=True)
        faiss.write_index(self.index, os.path.join(self.persist_dir, "faiss_index.bin"))
        with open(os.path.join(self.persist_dir, "image_metadata.json"), 'w', encoding='utf-8') as f:
            json.dump(self.metadatas, f, ensure_ascii=False, indent=2)
        with open(os.path.join(self.persist_dir, "image_features.pkl"), 'wb') as f:
            pickle.dump(self.features, f)
        print("[RETRIEVER] 已保存至: %s" % self.persist_dir)

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict]:
        """执行向量搜索"""
        if self.index is None:
            print("[ERROR] 索引未加载！")
            return []

        q = query_vector.astype(np.float32).reshape(1, -1)

        # 维度对齐
        if q.shape[1] != self.dim:
            print("[WARN] 查询维度(%d)与索引维度(%d)不匹配" % (q.shape[1], self.dim))
            if q.shape[1] < self.dim:
                q = np.concatenate([q, np.zeros((1, self.dim - q.shape[1]), dtype=np.float32)], axis=1)
            else:
                q = q[:, :self.dim]

        faiss.normalize_L2(q)
        k = min(k, self.index.ntotal)
        scores, indices = self.index.search(q, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.metadatas):
                meta = self.metadatas[idx]
                results.append({
                    "filename": meta.get("filename", "unknown"),
                    "filepath": meta.get("filepath", ""),
                    "score": float(score),
                    "feature_idx": int(idx),
                })
        return results

    def search_by_text(self, text: str, encoder, k: int = 5) -> List[Dict]:
        """文本搜索: 编码文本 → 向量搜索"""
        text_vec = encoder.encode_text(text)
        return self.search(text_vec, k)

    def search_by_image(self, image_path: str, encoder, k: int = 5) -> List[Dict]:
        """以图搜图: 编码图片 → 向量搜索"""
        result = encoder.encode_image(image_path)
        return self.search(result, k)


if __name__ == "__main__":
    print("=== 测试VisualRetriever ===")
    retriever = VisualRetriever()
    retriever.load("./index")

    from image_encoder import ImageEncoder
    encoder = ImageEncoder(mode="pixel")

    # 文本搜索
    results = retriever.search_by_text("red", encoder, k=3)
    print("\n文本搜索 'red':")
    for r in results:
        print("  %s (%.4f)" % (r["filename"], r["score"]))

    # 以图搜图
    results2 = retriever.search_by_image("./images/img_01.png", encoder, k=3)
    print("\n以图搜图 img_01.png:")
    for r in results2:
        print("  %s (%.4f)" % (r["filename"], r["score"]))

    print("\n测试完成！")