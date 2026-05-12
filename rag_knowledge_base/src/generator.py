"""
生成器模块
构造 Prompt 并调用大语言模型生成回答
支持 OpenAI 兼容 API（阿里云 Qwen-Plus、OpenAI GPT-4o-mini 等）
纯 Python 实现，不依赖 langchain
"""
import os
from typing import Optional, List, Dict


class RAGGenerator:
    """
    基于 OpenAI 兼容 API 的 RAG 回答生成器
    支持：阿里云 Qwen-Plus, OpenAI GPT-4o-mini, GPT-4o 等
    自动适配 openai SDK 新旧版本
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "qwen-plus",
                 base_url: Optional[str] = None):
        """
        Args:
            api_key: API 密钥，优先使用传入参数，若为空则读取环境变量
            model: 使用的模型名称
            base_url: API 基础 URL，若不指定则使用 DashScope 地址
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "") or os.environ.get("DASHSCOPE_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "API Key 未设置！\n"
                "请通过以下方式之一配置：\n"
                "  1. 传入 api_key 参数\n"
                "  2. 设置环境变量: export DASHSCOPE_API_KEY='your-key'\n"
                "  3. 设置环境变量: export OPENAI_API_KEY='your-key'"
            )
        self.model = model
        self.base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"

        # 适配 openai SDK 新旧版本
        import openai
        if hasattr(openai, 'OpenAI'):
            # 新版 SDK (1.0+)
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self._use_new_api = True
        else:
            # 旧版 SDK (0.x)
            openai.api_key = self.api_key
            openai.api_base = self.base_url
            self._use_new_api = False

    def generate(self, query: str, context_texts: List[Dict[str, str]], top_k: int = 4) -> Dict:
        """
        基于问题和检索到的上下文生成回答

        Args:
            query: 用户问题
            context_texts: [{"source": "...", "content": "..."}, ...]
            top_k: 参与生成的最大上下文数量

        Returns:
            dict: 包含 'answer' 和 'sources' 的字典
        """
        # 构建上下文字符串
        context_parts = []
        for ctx in context_texts[:top_k]:
            context_parts.append(
                "=== 来源: %s ===\n%s\n" % (ctx['source'], ctx['content'])
            )
        context_str = "\n".join(context_parts)

        prompt = """你是一个专业的企业知识库问答助手。请根据下面的内部文档内容，回答用户的问题。

【重要规则】
1. 回答必须严格基于提供的文档内容，不要编造任何信息。
2. 如果文档中没有相关信息，请回答："抱歉，我没有在知识库中找到与问题相关的信息，请联系相关负责人。"
3. 回答应当清晰、准确、有条理，适当使用分段和列表。
4. 避免使用模糊表述，如"可能"、"大概"等。
5. 回答末尾列出所引用的文档来源。

【检索到的文档内容】
%s

【用户问题】
%s

请给出你的回答：""" % (context_str, query)

        try:
            if self._use_new_api:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的企业知识库问答助手，只基于给定文档回答问题。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                answer = response.choices[0].message.content
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的企业知识库问答助手，只基于给定文档回答问题。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                answer = response['choices'][0]['message']['content']

            sources = [ctx["source"] for ctx in context_texts[:top_k]]
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            return {
                "answer": "生成回答时出现错误: %s" % str(e),
                "sources": []
            }


class MockGenerator:
    """Mock 生成器：未配置 API Key 时使用，直接返回检索结果"""

    def generate(self, query: str, context_texts: List[Dict[str, str]], top_k: int = 4) -> Dict:
        context_parts = []
        for ctx in context_texts[:top_k]:
            context_parts.append(
                "=== 来源: %s ===\n%s\n" % (ctx['source'], ctx['content'])
            )
        context_str = "\n".join(context_parts)

        return {
            "answer": (
                "【未配置 API Key】\n\n"
                "当前仅展示检索到的上下文内容，请配置 API Key 以启用 AI 生成回答。\n"
                "设置方式：export DASHSCOPE_API_KEY='your-key'\n\n"
                "---检索到的上下文---\n\n%s" % context_str
            ),
            "sources": [ctx["source"] for ctx in context_texts[:top_k]]
        }


def create_generator(provider: str = "auto", **kwargs) -> object:
    """
    工厂方法：创建生成器实例

    Args:
        provider: "qwen" | "openai" | "auto"
        **kwargs: api_key, model, base_url 等

    Returns:
        RAGGenerator 或 MockGenerator
    """
    api_key = (kwargs.get("api_key") or
               os.environ.get("DASHSCOPE_API_KEY") or
               os.environ.get("OPENAI_API_KEY"))

    if not api_key:
        print("[WARN] 未检测到 API Key，将使用 Mock 模式（仅展示检索内容）")
        return MockGenerator()

    if provider == "openai":
        return RAGGenerator(
            api_key=api_key,
            model=kwargs.get("model", "gpt-4o-mini"),
            base_url=kwargs.get("base_url", "https://api.openai.com/v1")
        )
    else:
        return RAGGenerator(
            api_key=api_key,
            model=kwargs.get("model", "qwen-plus"),
            base_url=kwargs.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        )


if __name__ == "__main__":
    print("本模块由 app.py 调用，不直接运行")