import os
import io
import base64
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

app = Flask(__name__)
CORS(app)

# 创建输出目录
os.makedirs("static/output", exist_ok=True)
os.makedirs("static/styles", exist_ok=True)

# 预设风格
STYLES = {
    "original": {"name": "原图", "filter": None},
    "sketch": {"name": "素描", "filter": "sketch"},
    "oil": {"name": "油画", "filter": "oil"},
    "watercolor": {"name": "水彩", "filter": "watercolor"},
    "vintage": {"name": "复古", "filter": "vintage"},
    "dramatic": {"name": "戏剧性", "filter": "dramatic"},
    "glow": {"name": "梦幻光晕", "filter": "glow"},
    "noir": {"name": "黑白电影", "filter": "noir"},
}

def apply_filter(img, filter_name):
    """应用不同的滤镜效果"""
    img = img.convert('RGB')

    if filter_name == "sketch":
        # 素描效果
        gray = img.convert('L')
        for _ in range(3):
            blur = gray.filter(ImageFilter.GaussianBlur(radius=2))
        edges = gray.filter(ImageFilter.FIND_EDGES)
        return edges.convert('RGB')

    elif filter_name == "oil":
        # 油画效果 - 增强色彩和对比
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.5)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)
        for _ in range(2):
            img = img.filter(ImageFilter.SMOOTH_MORE)
        return img

    elif filter_name == "watercolor":
        # 水彩效果 - 柔和色彩
        for _ in range(2):
            img = img.filter(ImageFilter.GaussianBlur(radius=1))
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.3)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)
        return img

    elif filter_name == "vintage":
        # 复古效果 - 偏黄褪色
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.8)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(0.9)
        # 添加暖色调
        arr = np.array(img)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.1, 0, 255)  # 红
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.9, 0, 255)  # 蓝
        return Image.fromarray(arr.astype('uint8'))

    elif filter_name == "dramatic":
        # 戏剧性效果 - 高对比度
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.8)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.2)
        return img

    elif filter_name == "glow":
        # 梦幻光晕
        blur = img.filter(ImageFilter.GaussianBlur(radius=5))
        enhancer = ImageEnhance.Brightness(blur)
        blur = enhancer.enhance(1.3)
        arr = np.array(img).astype('float') * 0.7 + np.array(blur).astype('float') * 0.3
        arr = np.clip(arr, 0, 255)
        return Image.fromarray(arr.astype('uint8'))

    elif filter_name == "noir":
        # 黑白电影效果
        gray = img.convert('L')
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(1.5)
        return gray.convert('RGB')

    return img

def image_to_base64(img):
    """图片转base64"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/styles', methods=['GET'])
def get_styles():
    """获取可用风格列表"""
    styles = []
    for key, value in STYLES.items():
        styles.append({"id": key, "name": value["name"]})
    return jsonify(styles)

@app.route('/apply-style', methods=['POST'])
def apply_style():
    """应用风格"""
    if 'image' not in request.files:
        return jsonify({"error": "请上传图片"}), 400

    file = request.files['image']
    style = request.form.get('style', 'original')

    if style not in STYLES:
        style = 'original'

    # 读取图片
    img = Image.open(file.stream)

    # 调整图片大小（处理大图片）
    max_size = 800
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # 应用风格
    if style != 'original':
        img = apply_filter(img, STYLES[style]["filter"])

    # 返回结果
    result_base64 = image_to_base64(img)

    return jsonify({
        "success": True,
        "style": style,
        "style_name": STYLES[style]["name"],
        "image": f"data:image/png;base64,{result_base64}"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("图像风格迁移系统已启动!")
    print("访问: http://localhost:5000")
    print("="*50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)