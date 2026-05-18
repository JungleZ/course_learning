"""
多模态视觉RAG应用 - Gradio交互界面
"""
import sys
import os
import warnings
import traceback
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import gradio as gr
import numpy as np
from PIL import Image

from image_encoder import ImageEncoder, auto_select_encoder
from retriever import VisualRetriever
from generator import create_generator
from data_processing import process_images, load_index

BASE_PROJECT_DIR = os.path.dirname(BASE_DIR)
IMAGE_DIR = os.path.join(BASE_PROJECT_DIR, "images")
INDEX_DIR = os.path.join(BASE_PROJECT_DIR, "index")

LOG_FILE = os.path.join(BASE_PROJECT_DIR, "app.log")

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

log("=" * 60)
log("[APP] Starting...")

encoder = None
retriever = None
generator_inst = None


def init_system():
    global encoder, retriever, generator_inst

    encoder = auto_select_encoder()
    print("[SYS] 编码器: %s (dim=%d)" % (encoder.mode, encoder.dim))

    need_rebuild = not os.path.exists(os.path.join(INDEX_DIR, "faiss_index.bin"))
    if need_rebuild:
        print("[SYS] 构建索引...")
        process_images(IMAGE_DIR, INDEX_DIR)

    retriever = VisualRetriever(persist_dir=INDEX_DIR, dim=encoder.dim)
    retriever.load(INDEX_DIR)

    generator_inst = create_generator()
    print("[SYS] 就绪！")


def rebuild_index():
    process_images(IMAGE_DIR, INDEX_DIR)
    retriever.load(INDEX_DIR)
    return "OK 已重建 (%d 张图片)" % retriever.index.ntotal


def search_by_text(query, top_k=5):
    try:
        if not query.strip() or retriever is None:
            return [], "请先输入关键词"

        log("[SEARCH] query: " + query.strip())
        results = retriever.search_by_text(query.strip(), encoder, k=top_k)
        log("[SEARCH] results: %d" % len(results))

        if not results:
            return [], "无匹配图片"

        images = []
        info = ""
        for i, r in enumerate(results):
            filepath = r["filepath"]
            log("[SEARCH] file: " + filepath)
            if os.path.exists(filepath):
                img = Image.open(filepath)
                images.append(np.array(img))
            else:
                log("[SEARCH] file not found: " + filepath)
            info += "%d. %s (%.4f)\n" % (i + 1, r["filename"], r["score"])

        return images, info
    except Exception as e:
        log("[SEARCH ERROR] " + str(e))
        log(traceback.format_exc())
        return [], "搜索出错: %s" % str(e)


def search_by_image(uploaded_image, top_k=5):
    try:
        if uploaded_image is None or retriever is None:
            return [], "请上传图片"

        log("[IMGSEARCH] input type: %s" % type(uploaded_image).__name__)

        if isinstance(uploaded_image, np.ndarray):
            img = Image.fromarray(uploaded_image)
        elif isinstance(uploaded_image, str):
            img = Image.open(uploaded_image)
        else:
            img = uploaded_image

        temp_path = os.path.join(INDEX_DIR, "_q.png")
        img.save(temp_path)
        log("[IMGSEARCH] saved query image: " + temp_path)

        results = retriever.search_by_image(temp_path, encoder, k=top_k)
        log("[IMGSEARCH] results: %d" % len(results))

        if not results:
            return [], "无相似图片"

        images = []
        info = ""
        for i, r in enumerate(results):
            filepath = r["filepath"]
            if os.path.exists(filepath):
                img = Image.open(filepath)
                images.append(np.array(img))
            info += "%d. %s (%.4f)\n" % (i + 1, r["filename"], r["score"])

        return images, info
    except Exception as e:
        log("[IMGSEARCH ERROR] " + str(e))
        log(traceback.format_exc())
        return [], "搜索出错: %s" % str(e)


def qa_with_images(query, uploaded_image, history, top_k=3):
    if not query.strip():
        return "", history

    query = query.strip()

    if uploaded_image is not None:
        if isinstance(uploaded_image, np.ndarray):
            img = Image.fromarray(uploaded_image)
        elif isinstance(uploaded_image, str):
            img = Image.open(uploaded_image)
        else:
            img = uploaded_image
        temp_path = os.path.join(INDEX_DIR, "_qa.png")
        img.save(temp_path)
        results = retriever.search_by_image(temp_path, encoder, k=top_k)
    else:
        results = retriever.search_by_text(query, encoder, k=top_k)

    img_paths = [r["filepath"] for r in results if os.path.exists(r["filepath"])]
    scores = [r["score"] for r in results if os.path.exists(r["filepath"])]

    qa_query = query if not uploaded_image else "[图片] " + query
    history.append((qa_query, "[*] 分析中..."))

    try:
        result = generator_inst.generate_from_images(query, img_paths, scores)
        sources = "\n".join(["  - %s" % img for img in result.get("images", [])])
        final = "%s\n\n---图片源---\n%s" % (result['answer'], sources)
        history[-1] = (qa_query, final)
    except Exception as e:
        history[-1] = (qa_query, "[错误] %s" % str(e))

    return "", history


with gr.Blocks(
    title="多模态视觉RAG",
    theme=gr.themes.Soft(),
) as demo:
    gr.HTML("""
    <div style="text-align:center; margin-bottom:15px">
        <h1>多模态视觉 RAG 系统</h1>
        <p style="color:#666">像素特征 + FAISS + GPT-4o (Mock模式)</p>
    </div>
    """)

    gr.HTML("""
    <div style="background:#f0f4ff; padding:15px; border-radius:8px; margin-bottom:15px; font-size:14px">
        <strong>指南：</strong><br/>
        1. <strong>文本搜图</strong> - 输入文字搜索相关图片<br/>
        2. <strong>以图搜图</strong> - 上传图片找相似图片<br/>
        3. <strong>视觉问答</strong> - 上传图片+提问，AI分析回答<br/>
        4. <strong>重建索引</strong> - 添加新图片后重建
    </div>
    """)

    with gr.Tabs():
        with gr.TabItem("文本搜图"):
            tq = gr.Textbox(label="搜索关键词", placeholder="例如：红色、几何图案...")
            tb = gr.Button("搜索", variant="primary")
            tg = gr.Gallery(label="结果", columns=[3], height="auto")
            ti = gr.Textbox(label="检索信息", lines=5)
            tb.click(search_by_text, [tq], [tg, ti])

        with gr.TabItem("以图搜图"):
            ig = gr.Image(label="上传参考图片", type="pil")
            ib = gr.Button("搜索相似", variant="primary")
            ig_res = gr.Gallery(label="相似图片", columns=[3], height="auto")
            ii = gr.Textbox(label="检索信息", lines=5)
            ib.click(search_by_image, [ig], [ig_res, ii])

        with gr.TabItem("视觉问答"):
            qa_img = gr.Image(label="上传图片（可选）", type="pil")
            qa_q = gr.Textbox(label="问题", placeholder="描述内容或提问...")
            qa_b = gr.Button("提问", variant="primary")
            qa_c = gr.Chatbot(label="对话", height=350)
            qa_b.click(qa_with_images, [qa_q, qa_img, qa_c], [qa_q, qa_c])

        with gr.TabItem("系统管理"):
            si = gr.Textbox(label="状态", value="就绪", interactive=False)
            rb = gr.Button("重建索引")
            rb.click(fn=lambda: rebuild_index(), inputs=[], outputs=[si])


if __name__ == "__main__":
    print("=" * 60)
    print("[APP] 多模态视觉RAG - 启动中...")
    print("=" * 60)
    init_system()
    print("\n[WEB] http://127.0.0.1:7861")
    print("=" * 60)
    
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7861,
        share=False
    )