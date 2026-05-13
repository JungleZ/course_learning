import os
import sys
import warnings

# 抑制所有 matplotlib 警告
warnings.filterwarnings('ignore')
os.environ['MATPLOTLIB_NONINTERACTIVE'] = '1'

# 确保 src 目录在 Python 路径中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import gradio as gr
from data_processing import process_documents, load_database
from retriever import create_retriever, is_off_topic, get_top_k_texts
from generator import create_generator

# ========== 路径配置 ==========
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")
DOC_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")

# ========== 全局状态 ==========
retriever = None
generator = None


def init_system():
    """初始化系统"""
    global retriever, generator

    # 1. 检查是否需要建库
    need_rebuild = (
        not os.path.exists(PERSIST_DIR) or
        not os.path.exists(os.path.join(PERSIST_DIR, "faiss_index.bin"))
    )

    if need_rebuild:
        print("[SYS] 向量数据库不存在，正在初始化...")
        process_documents(DOC_DIR, PERSIST_DIR)

    # 2. 加载检索器
    retriever = create_retriever(PERSIST_DIR, k=4)
    print("[SYS] 检索器已就绪（%d 个向量）" % retriever['index'].ntotal)

    # 3. 创建生成器
    generator = create_generator()
    print("[SYS] 生成器已就绪")


def rebuild_database():
    """重新构建数据库"""
    global retriever
    result = process_documents(DOC_DIR, PERSIST_DIR)
    if result:
        retriever = create_retriever(PERSIST_DIR, k=4)
        return "OK 数据库已重建完成！"
    return "FAIL 数据库重建失败，请检查 data/ 目录"


def answer_question(user_question, history):
    """Gradio 对话回调函数"""
    if not user_question or not user_question.strip():
        return "", history

    user_question = user_question.strip()

    # 检查是否为离题问题
    if is_off_topic(user_question):
        history.append((user_question,
            "[!] 这个问题超出了企业知识库的范围。\n\n"
            "我只能回答关于公司制度、技术规范、产品FAQ、项目总结等方面的问题。\n"
            "请勿询问天气、新闻、娱乐等与工作无关的话题。"))
        return "", history

    history.append((user_question, "[*] 正在检索和生成回答..."))

    try:
        # 1. 使用 FAISS + TF-IDF 检索
        top_k_texts = get_top_k_texts(user_question, PERSIST_DIR, k=4)

        if not top_k_texts:
            history[-1] = (user_question, "抱歉，我没有在知识库中找到相关信息，请联系相关负责人。")
            return "", history

        # 构建上下文
        context_texts = [
            {"source": source, "content": content}
            for source, content, score in top_k_texts
        ]

        # 2. 生成回答
        result = generator.generate(user_question, context_texts)

        # 3. 构造带参考来源的回答
        sources_text = "\n".join(["  - " + s for s in result.get("sources", [])])
        final_answer = "%s\n\n---\n【参考来源】\n%s" % (result['answer'], sources_text)

        history[-1] = (user_question, final_answer)

    except Exception as e:
        history[-1] = (user_question, "[ERROR] 处理过程中出现错误: %s" % str(e))

    return "", history


# ========== Gradio 界面 ==========
with gr.Blocks(
    title="企业智能知识库问答助手",
    theme=gr.themes.Soft(),
) as demo:
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1>企业智能知识库问答助手</h1>
        <p style="color: #666; font-size: 16px;">
            基于 RAG 技术 | 支持 Markdown/Word/PDF 文档 | 答案溯源
        </p>
    </div>
    """)

    gr.HTML("""
    <div style="background-color: #f0f4ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 14px;">
        <strong>使用指南：</strong>您可以询问关于<strong>公司制度、技术规范、产品FAQ、项目总结</strong>等方面的问题。<br/>
        <strong>注意：</strong>本系统仅回答企业内部知识问题，闲聊、天气、新闻等话题将被拒绝。
    </div>
    """)

    chatbot = gr.Chatbot(
        label="对话区域",
        height=450,
        show_copy_button=True,
        bubble_full_width=False,
    )

    with gr.Row():
        msg = gr.Textbox(
            label="输入您的问题",
            placeholder="例如：年度调薪的流程是什么？ / 员工手册里关于考勤有哪些规定？",
            scale=4,
            container=False,
            lines=2,
        )
        submit_btn = gr.Button("发送", variant="primary", scale=1, min_width=100)

    with gr.Row():
        clear_btn = gr.Button("清空对话", variant="secondary")
        rebuild_btn = gr.Button("重建知识库", variant="secondary")
        status_box = gr.Textbox(label="系统状态", value="就绪", interactive=False, scale=2)

    # 绑定事件
    msg.submit(fn=answer_question, inputs=[msg, chatbot], outputs=[msg, chatbot])
    submit_btn.click(fn=answer_question, inputs=[msg, chatbot], outputs=[msg, chatbot])
    clear_btn.click(fn=lambda: ([],), inputs=[], outputs=[chatbot])
    rebuild_btn.click(fn=lambda: rebuild_database(), inputs=[], outputs=[status_box])


# ========== 启动 ==========
if __name__ == "__main__":
    print("=" * 50)
    print("[APP] 企业智能知识库问答助手 - 启动中...")
    print("=" * 50)
    init_system()
    print("\n[WEB] 启动 Gradio 服务...")
    print("   本地地址: http://127.0.0.1:7860")
    print("=" * 50)
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)