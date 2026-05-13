"""
多模态视觉 RAG 系统
完全免费方案：像素特征 + FAISS + GPT-4o (可选API)
"""
import os
import sys
import json
import pickle
import numpy as np
import faiss
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
INDEX_FILE = "faiss_index.bin"
FEATURE_FILE = "image_features.pkl"
METADATA_FILE = "image_metadata.json"


def _get_image_files(img_dir: str) -> list:
    """获取目录下的所有图片文件"""
    files = []
    for root, _, filenames in os.walk(img_dir):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                files.append(os.path.join(root, filename))
    return files


def _extract_pixel_features(image_path: str, target_size: tuple = (224, 224)) -> np.ndarray:
    """
    提取图片的像素特征向量 (完全免费, 无需GPU)
    使用 resize + 颜色直方图 + 空间分布 + 纹理 + 统计特征
    """
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize(target_size)
        arr = np.array(img, dtype=np.float32) / 255.0

        features = []

        # 1. 全局颜色直方图 (每个通道16个bin = 48维)
        for i in range(3):
            hist, _ = np.histogram(arr[:, :, i], bins=16, range=(0, 1))
            total = hist.sum()
            features.extend((hist / max(total, 1)).tolist())

        # 2. 空间颜色分布 (4个象限的颜色均值 = 12维)
        h, w = arr.shape[:2]
        half_h, half_w = h // 2, w // 2
        for y_start, y_end in [(0, half_h), (half_h, h)]:
            for x_start, x_end in [(0, half_w), (half_w, w)]:
                patch = arr[y_start:y_end, x_start:x_end]
                features.extend(patch.mean(axis=(0, 1)).tolist())

        # 3. 纹理特征 (梯度直方图, 修复维度对齐bug)
        gray = arr.mean(axis=2)
        dx = np.diff(gray, axis=1)  # shape: (h, w-1)
        dy = np.diff(gray, axis=0)  # shape: (h-1, w)
        # 裁剪到相同尺寸
        min_h = min(dx.shape[0], dy.shape[0])
        min_w = min(dx.shape[1], dy.shape[1])
        dx_c = dx[:min_h, :min_w]
        dy_c = dy[:min_h, :min_w]
        grad_mag = np.sqrt(dx_c**2 + dy_c**2)
        gmax = grad_mag.max()
        if gmax > 0:
            hist_grad, _ = np.histogram(grad_mag, bins=16, range=(0, gmax))
        else:
            hist_grad = np.zeros(16)
        features.extend((hist_grad / max(hist_grad.sum(), 1)).tolist())

        # 4. 边缘密度
        features.append(float((grad_mag > 0.1).mean()))

        # 5. 亮度统计
        features.append(float(arr.mean()))
        features.append(float(arr.std()))

        # 6. 宽高比
        features.append(float(w / max(h, 1)))

        # 7. 饱和度均值
        hsv = np.stack([
            np.max(arr, axis=2),  # V通道近似
            np.min(arr, axis=2),
        ], axis=-1)
        saturation = (hsv[:, :, 0] - hsv[:, :, 1]) / max(hsv[:, :, 0].max(), 1e-8)
        features.append(float(saturation.mean()))

        return np.array(features, dtype=np.float32)
    except Exception as e:
        print("  [WARN] 处理图片失败 %s: %s" % (image_path, e))
        return None


def _reduce_dimension(features: np.ndarray, target_dim: int = 128) -> np.ndarray:
    """PCA降维 (简化版随机投影, 不依赖sklearn)"""
    n = len(features)
    if n <= target_dim:
        result = np.zeros(target_dim, dtype=np.float32)
        result[:n] = features
        return result

    # 随机高斯投影 (Johnson-Lindenstrauss)
    np.random.seed(42)
    projection = np.random.randn(target_dim, n).astype(np.float32)
    norm = np.linalg.norm(projection, axis=1, keepdims=True)
    norm[norm == 0] = 1
    projection /= norm
    return (projection @ features).astype(np.float32)


def process_images(image_dir: str = "./images", persist_dir: str = "./index"):
    """
    批量处理图片: 提取特征 → FAISS索引
    """
    print("=" * 60)
    print("[VISUAL RAG] 开始构建视觉知识库...")
    print("=" * 60)

    os.makedirs(persist_dir, exist_ok=True)

    # 1. 获取图片列表
    image_files = _get_image_files(image_dir)
    print("\n[FILES] 在 %s 中找到 %d 张图片:" % (image_dir, len(image_files)))
    for f in image_files:
        print("   - %s" % os.path.basename(f))

    if len(image_files) == 0:
        print("\n[WARN] 没有找到任何图片文件!")
        print("   请将图片放入 %s 目录" % image_dir)
        print("   支持格式: jpg, jpeg, png, gif, bmp, webp")
        return None

    # 2. 提取特征
    print("\n[FEATURES] 正在提取图片特征...")
    all_features = []
    all_metadatas = []

    for filepath in image_files:
        feat = _extract_pixel_features(filepath)
        if feat is not None:
            reduced = _reduce_dimension(feat, target_dim=128)
            all_features.append(reduced)
            all_metadatas.append({
                "filename": os.path.basename(filepath),
                "filepath": os.path.abspath(filepath),
                "filesize": os.path.getsize(filepath),
                "feature_dim": len(reduced),
            })
            print("   OK %s (%d dim)" % (os.path.basename(filepath), len(reduced)))

    if len(all_features) == 0:
        print("[FAIL] 所有图片处理失败")
        return None

    # 3. 构建FAISS索引
    print("\n[INDEX] 正在构建FAISS索引...")
    features_matrix = np.array(all_features, dtype=np.float32)
    faiss.normalize_L2(features_matrix)

    dim = features_matrix.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(features_matrix)

    print("   索引维度: %d" % dim)
    print("   图片数量: %d" % index.ntotal)

    # 4. 持久化
    faiss.write_index(index, os.path.join(persist_dir, INDEX_FILE))
    with open(os.path.join(persist_dir, FEATURE_FILE), 'wb') as f:
        pickle.dump(features_matrix, f)
    with open(os.path.join(persist_dir, METADATA_FILE), 'w', encoding='utf-8') as f:
        json.dump(all_metadatas, f, ensure_ascii=False, indent=2)

    print("\n[OK] 索引已保存至: %s" % persist_dir)
    print("   - %s" % INDEX_FILE)
    print("   - %s" % FEATURE_FILE)
    print("   - %s" % METADATA_FILE)
    print("=" * 60)

    return index, all_metadatas, features_matrix


def load_index(persist_dir: str = "./index"):
    """从磁盘加载索引"""
    index = faiss.read_index(os.path.join(persist_dir, INDEX_FILE))
    with open(os.path.join(persist_dir, FEATURE_FILE), 'rb') as f:
        features = pickle.load(f)
    with open(os.path.join(persist_dir, METADATA_FILE), 'r', encoding='utf-8') as f:
        metadatas = json.load(f)
    print("[OK] 索引已加载: %d 张图片" % index.ntotal)
    return index, metadatas, features


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(base)
    image_dir = os.path.join(project_dir, "images")
    persist_dir = os.path.join(project_dir, "index")

    # 处理并保存
    process_images(image_dir, persist_dir)

    # 然后加载验证
    print("\n验证加载...")
    idx, meta, feat = load_index(persist_dir)
    print("共 %d 张图片, 特征维度 %d" % (idx.ntotal, feat.shape[1]))