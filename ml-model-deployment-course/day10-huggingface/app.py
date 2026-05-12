"""
Day 10: HuggingFace Spaces 部署 - 文本分类 Demo

功能：
1. 中文情感分析
2. 英文情感分析
3. 文本生成

运行方式：
    python app.py

部署到 HuggingFace Spaces：
    1. 创建 Space，选择 Gradio SDK
    2. 上传 app.py 和 requirements.txt
"""

import gradio as gr
from transformers import pipeline
import os

# 设置缓存目录
os.environ["TRANSFORMERS_CACHE"] = "./model_cache"

print("⏳ 正在加载模型，首次运行需要下载（约1-2分钟）...")

# ========== 加载模型 ==========

# 中文情感分析模型
chinese_sentiment = pipeline(
    "text-classification",
    model="uer/roberta-base-finetuned-jd-binary-chinese"
)

# 英文情感分析模型
english_sentiment = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# 文本生成模型
text_generator = pipeline(
    "text-generation",
    model="distilgpt2"
)

print("✅ 模型加载完成！")


# ========== 预测函数 ==========

def analyze_chinese_sentiment(text):
    """中文情感分析"""
    if not text.strip():
        return {"错误": 1.0}, ""
    
    result = chinese_sentiment(text)[0]
    
    # 映射标签
    label_map = {
        "positive": "正面 😊",
        "negative": "负面 😞",
        "POSITIVE": "正面 😊",
        "NEGATIVE": "负面 😞",
        "LABEL_0": "负面 😞",
        "LABEL_1": "正面 😊",
        "1": "正面 😊",
        "0": "负面 😞"
    }
    
    label = label_map.get(result["label"], result["label"])
    
    return {label: result["score"]}, f"原始标签：{result['label']}，置信度：{result['score']:.4f}"


def analyze_english_sentiment(text):
    """英文情感分析"""
    if not text.strip():
        return {"错误": 1.0}, ""
    
    result = english_sentiment(text)[0]
    label_map = {
        "POSITIVE": "Positive 😊",
        "NEGATIVE": "Negative 😞"
    }
    
    label = label_map.get(result["label"], result["label"])
    
    return {label: result["score"]}, f"Label: {result['label']}, Score: {result['score']:.4f}"


def generate_text(prompt, max_length=100):
    """文本生成"""
    if not prompt.strip():
        return "请输入提示文本"
    
    result = text_generator(
        prompt,
        max_length=max_length,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7
    )
    
    return result[0]["generated_text"]


# ========== 构建 Gradio 界面 ==========

with gr.Blocks(title="🤗 HuggingFace ML Demo", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown(
        """
        # 🤗 HuggingFace ML Demo
        基于 Transformer 模型的 AI 应用演示
        """
    )
    
    with gr.Tab("🇨🇳 中文情感分析"):
        gr.Markdown("输入中文文本，分析情感倾向（正面/负面）")
        
        cn_input = gr.Textbox(
            label="输入中文文本",
            placeholder="例如：这个产品非常好用，我很喜欢！",
            lines=3
        )
        cn_label = gr.Label(label="情感分析结果")
        cn_detail = gr.Textbox(label="详细信息")
        
        cn_btn = gr.Button("🔍 分析情感", variant="primary")
        cn_btn.click(
            fn=analyze_chinese_sentiment,
            inputs=cn_input,
            outputs=[cn_label, cn_detail]
        )
        
        gr.Examples(
            examples=[
                "这个产品非常好用，我很喜欢！",
                "质量太差了，非常失望。",
                "今天天气不错，心情很好。",
                "这部电影太无聊了，浪费时间和金钱。",
                "服务态度很好，下次还会来。"
            ],
            inputs=cn_input
        )
    
    with gr.Tab("🇬🇧 英文情感分析"):
        gr.Markdown("Enter English text for sentiment analysis")
        
        en_input = gr.Textbox(
            label="Enter English text",
            placeholder="e.g., I love this movie! It's amazing!",
            lines=3
        )
        en_label = gr.Label(label="Sentiment Result")
        en_detail = gr.Textbox(label="Details")
        
        en_btn = gr.Button("🔍 Analyze Sentiment", variant="primary")
        en_btn.click(
            fn=analyze_english_sentiment,
            inputs=en_input,
            outputs=[en_label, en_detail]
        )
        
        gr.Examples(
            examples=[
                "I love this movie! It's amazing!",
                "This product is terrible. Waste of money.",
                "The weather is beautiful today.",
                "I'm so disappointed with the service."
            ],
            inputs=en_input
        )
    
    with gr.Tab("✍️ 文本生成"):
        gr.Markdown("输入提示文本，AI 续写内容")
        
        gen_input = gr.Textbox(
            label="提示文本 (Prompt)",
            placeholder="Once upon a time",
            lines=2
        )
        gen_max_length = gr.Slider(50, 200, value=100, step=10, label="最大长度")
        gen_output = gr.Textbox(label="生成结果", lines=5)
        
        gen_btn = gr.Button("✍️ 生成文本", variant="primary")
        gen_btn.click(
            fn=generate_text,
            inputs=[gen_input, gen_max_length],
            outputs=gen_output
        )
        
        gr.Examples(
            examples=[
                "Once upon a time",
                "The future of AI is",
                "In the year 2050,",
                "The most important thing in life is"
            ],
            inputs=gen_input
        )


# ========== 启动 ==========
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860
    )
