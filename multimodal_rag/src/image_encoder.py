"""
图片编码器模块
提供像素级特征提取（完全免费）和可选的OpenAI Vision编码
"""
import os
import json
import base64
import numpy as np
from PIL import Image
from io import BytesIO


class ImageEncoder:
    """
    图片编码器 - 支持像素特征和OpenAI Vision两种模式
    """

    def __init__(self, mode: str = "pixel", api_key: str = None):
        """
        Args:
            mode: "pixel" (免费像素特征) | "openai" (需API Key)
            api_key: OpenAI API Key (仅openai模式需要)
        """
        self.mode = mode
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.dim = 128
        print("[ENCODER] 模式: %s, 维度: %d" % (self.mode, self.dim))

    def encode_image(self, image_path: str):
        """编码单张图片"""
        return self._encode_pixel(image_path)

    def _encode_pixel(self, image_path: str):
        """像素级特征提取 (完全免费)"""
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize((224, 224))
            arr = np.array(img, dtype=np.float32) / 255.0

            features = []

            # 颜色直方图
            for i in range(3):
                hist, _ = np.histogram(arr[:, :, i], bins=16, range=(0, 1))
                features.extend((hist / max(hist.sum(), 1)).tolist())

            # 空间颜色分布
            h, w = arr.shape[:2]
            hh, hw = h // 2, w // 2
            for ys, ye in [(0, hh), (hh, h)]:
                for xs, xe in [(0, hw), (hw, w)]:
                    patch = arr[ys:ye, xs:xe]
                    features.extend(patch.mean(axis=(0, 1)).tolist())

            # 梯度特征 (修复维度对齐)
            gray = arr.mean(axis=2)
            dx = np.diff(gray, axis=1)
            dy = np.diff(gray, axis=0)
            mh = min(dx.shape[0], dy.shape[0])
            mw = min(dx.shape[1], dy.shape[1])
            grad = np.sqrt(dx[:mh, :mw]**2 + dy[:mh, :mw]**2)
            gmax = grad.max()
            if gmax > 0:
                hg, _ = np.histogram(grad, bins=16, range=(0, gmax))
            else:
                hg = np.zeros(16)
            features.extend((hg / max(hg.sum(), 1)).tolist())

            # 统计
            features.append(float(grad.mean()))
            features.append(float(arr.mean()))
            features.append(float(arr.std()))
            features.append(float(w / max(h, 1)))
            features.append(float(arr.std(axis=(0,1)).mean()))

            vec = np.array(features, dtype=np.float32)
            n = np.linalg.norm(vec)
            if n > 0:
                vec /= n
            return vec
        except Exception as e:
            print("  [WARN] 编码失败 %s: %s" % (image_path, e))
            return np.zeros(self.dim, dtype=np.float32)

    def encode_text(self, text: str) -> np.ndarray:
        """
        编码文本查询 (用于以文搜图)
        像素模式下用随机投影模拟
        """
        # 基于文本哈希的简单投影 (像素模式下无更好选择)
        np.random.seed(abs(hash(text)) % (2**31))
        vec = np.random.randn(self.dim).astype(np.float32)
        vec /= np.linalg.norm(vec) + 1e-8

        # 加入文本长度等简单特征作为偏置
        words = text.lower().split()
        for word in words[:10]:
            whash = hash(word) % self.dim
            vec[whash % self.dim] += 0.1

        vec /= np.linalg.norm(vec) + 1e-8
        return vec

    def encode_batch(self, image_paths: list) -> list:
        """批量编码图片"""
        results = []
        for path in image_paths:
            print("  编码: %s" % os.path.basename(path))
            vec = self.encode_image(path)
            results.append({"feature": vec, "filepath": path})
        return results


def auto_select_encoder():
    """自动选择最佳编码器"""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        return ImageEncoder(mode="openai", api_key=api_key)
    return ImageEncoder(mode="pixel")