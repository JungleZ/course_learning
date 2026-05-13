"""
多模态生成器
基于GPT-4o的多模态问答生成 (支持Mock模式)
"""
import os
from typing import List, Dict


class VisualGenerator:
    """基于GPT-4o的视觉问答生成器"""

    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            import openai
            openai.api_key = self.api_key
            self._client = openai
        return self._client

    def generate_from_images(self, query: str, image_paths: List[str],
                              image_scores: List[float] = None) -> Dict:
        if image_scores is None:
            image_scores = [1.0] * len(image_paths)

        import base64
        client = self._get_client()

        image_messages = []
        for path in image_paths:
            try:
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                ext = os.path.splitext(path)[1].lower().replace(".", "")
                if ext == "jpg":
                    ext = "jpeg"
                image_messages.append({
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/%s;base64,%s" % (ext, b64),
                        "detail": "auto"
                    }
                })
            except Exception as e:
                image_messages.append({
                    "type": "text",
                    "text": "[无法加载: %s]" % os.path.basename(path)
                })

        messages = [
            {"role": "system", "content": "你是一个视觉分析专家。根据图片和问题给出回答，不要编造信息。"},
            {"role": "user", "content": [
                {"type": "text", "text": "问题: %s\n\n相关图片 (%d张):" % (query, len(image_paths))}
            ] + image_messages}
        ]

        try:
            response = client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            answer = response.choices[0].message.content
            return {
                "answer": answer,
                "images": [os.path.basename(p) for p in image_paths],
                "model": self.model,
            }
        except Exception as e:
            return {
                "answer": "[GPT-4o错误: %s]" % str(e),
                "images": [os.path.basename(p) for p in image_paths],
            }


class MockGenerator:
    """Mock生成器 - 不依赖API"""

    def generate_from_images(self, query: str, image_paths: List[str],
                              image_scores: List[float] = None) -> Dict:
        if image_scores is None:
            image_scores = [1.0] * len(image_paths)

        result = "=== Mock模式（未配置API Key）===\n\n"
        result += "查询: %s\n\n" % query
        result += "检索到的图片:\n"
        for path, score in zip(image_paths, image_scores):
            result += "  - %s (相关度: %.4f)\n" % (os.path.basename(path), score)
        result += "\n提示: 设置 OPENAI_API_KEY 启用AI生成回答"

        return {
            "answer": result,
            "images": [os.path.basename(p) for p in image_paths],
            "model": "MOCK",
        }


def create_generator(api_key: str = None):
    """工厂方法"""
    key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if key:
        print("[GEN] GPT-4o 模式")
        return VisualGenerator(api_key=key)
    else:
        print("[GEN] Mock模式 (无API Key)")
        return MockGenerator()