import sys
print("Python:", sys.version)

try:
    import torch
    print("torch:", torch.__version__)
except:
    print("torch: 未安装")

try:
    import clip
    print("clip: 已安装")
except:
    print("clip: 未安装")

try:
    import faiss
    print("faiss:", faiss.__version__)
except:
    print("faiss: 未安装")

try:
    from PIL import Image
    import PIL
    print("Pillow:", PIL.__version__)
except:
    print("Pillow: 未安装")

try:
    import openai
    print("openai:", openai.__version__)
except:
    print("openai: 未安装")

try:
    import gradio as gr
    print("gradio:", gr.__version__)
except:
    print("gradio: 未安装")

try:
    import numpy as np
    print("numpy:", np.__version__)
except:
    print("numpy: 未安装")