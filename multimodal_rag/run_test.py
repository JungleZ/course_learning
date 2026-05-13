"""端到端全流程测试"""
import sys
import os
import warnings
warnings.filterwarnings('ignore')

os.chdir("D:\\code_workspaces\\multimodal_rag")
sys.path.insert(0, 'src')

print("=" * 60)
print("多模态视觉RAG - 全流程测试")
print("=" * 60)

# 1. 建库
print("\n[1/5] 构建图片索引...")
from src.data_processing import process_images, load_index
result = process_images('./images', './index')
if result is None:
    print("FAIL"); sys.exit(1)
idx, meta, feat = result
print("   OK: %d张图片已索引" % len(meta))

# 2. 加载检索器
print("\n[2/5] 加载检索器...")
from src.retriever import VisualRetriever
retriever = VisualRetriever(persist_dir='./index', dim=128)
retriever.load('./index')
print("   OK: %d张图片就绪" % retriever.index.ntotal)

# 3. 编码器
print("\n[3/5] 初始化编码器...")
from src.image_encoder import ImageEncoder
enc = ImageEncoder(mode='pixel')
print("   OK: 模式=%s, 维度=%d" % (enc.mode, enc.dim))

# 4. 文本搜图
print("\n[4/5] 文本搜索测试...")
results = retriever.search_by_text("red", enc, k=3)
print("   查询: 'red'")
for r in results:
    print("   -> %s (%.4f)" % (r["filename"], r["score"]))

# 5. 以图搜图
print("\n[5/5] 以图搜图测试...")
results2 = retriever.search_by_image("./images/img_01.png", enc, k=3)
print("   查询: img_01.png")
for r in results2:
    print("   -> %s (%.4f)" % (r["filename"], r["score"]))

# 6. Mock问答
print("\n[6/5] Mock问答测试...")
from src.generator import MockGenerator
gen = MockGenerator()
paths = [r["filepath"] for r in results2[:2] if os.path.exists(r["filepath"])]
qa = gen.generate_from_images("what colors and shapes?", paths)
print("   问题: 'what colors and shapes?'")
print("   回答:\n%s" % qa["answer"][:200])

# 7. Gradio导入测试
print("\n[7/5] Gradio导入测试...")
import gradio as gr
print("   OK: gradio %s" % gr.__version__)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)