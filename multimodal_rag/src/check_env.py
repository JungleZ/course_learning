"""
多模态视觉 RAG 系统
完全免费方案：CLIP/OpenAI Vision + FAISS + GPT-4o
"""
import sys
import os

# 检查可用依赖
print("=== 环境检测 ===")

# 检查torch
try:
    import torch
    print("torch:", torch.__version__)
    HAS_TORCH = True
except ImportError:
    print("torch: 未安装")
    HAS_TORCH = False

# 检查PIL
try:
    from PIL import Image
    import PIL
    print("Pillow:", PIL.__version__)
    HAS_PIL = True
except ImportError:
    print("Pillow: 未安装")
    HAS_PIL = False

# 检查CLIP
try:
    import clip
    print("clip: 已安装")
    HAS_CLIP = True
except ImportError:
    print("clip: 未安装")
    HAS_CLIP = False

# 检查OpenAI
try:
    import openai
    print("openai:", openai.__version__)
    HAS_OPENAI = True
except ImportError:
    print("openai: 未安装")
    HAS_OPENAI = False

# 检查FAISS
try:
    import faiss
    print("faiss:", faiss.__version__)
    HAS_FAISS = True
except ImportError:
    print("faiss: 未安装")
    HAS_FAISS = False

# 检查sklearn
try:
    import sklearn
    print("sklearn:", sklearn.__version__)
    HAS_SKLEARN = True
except ImportError:
    print("sklearn: 未安装")
    HAS_SKLEARN = False

print("\n系统: Python", sys.version.split()[0])

if not HAS_TORCH:
    print("\n⚠️  建议安装 PyTorch 来使用 CLIP 本地模型 (pip install torch torchvision)")
    print("   或者使用 OpenAI API 作为备选")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print("\n项目目录:", BASE_DIR)