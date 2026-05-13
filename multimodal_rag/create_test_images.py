"""生成示例测试图片 (纯英文标签)"""
import os
from PIL import Image, ImageDraw
import random

img_dir = "D:\\code_workspaces\\multimodal_rag\\images"
os.makedirs(img_dir, exist_ok=True)

colors = [(220, 80, 80), (80, 200, 80), (80, 100, 220),
          (220, 220, 80), (220, 80, 220), (80, 220, 220),
          (200, 150, 50), (50, 150, 200)]

labels = ["red_geo", "green_circle", "blue_square", "yellow_pattern",
          "purple_gradient", "cyan_texture", "orange_abstract", "blue_wave"]

for i in range(8):
    img = Image.new('RGB', (400, 300), color=colors[i])
    draw = ImageDraw.Draw(img)

    # 画随机形状
    for _ in range(random.randint(3, 8)):
        x1, y1 = random.randint(20, 350), random.randint(50, 250)
        x2 = x1 + random.randint(30, 100)
        y2 = y1 + random.randint(30, 100)
        c = colors[random.randint(0, len(colors)-1)]
        if i % 2 == 0:
            draw.rectangle([x1, y1, x2, y2], fill=c, outline=(0,0,0))
        else:
            draw.ellipse([x1, y1, x2, y2], fill=c, outline=(0,0,0))

    # 英文标签
    draw.rectangle([0, 0, 399, 30], fill=(0, 0, 0))
    draw.text((5, 5), labels[i], fill=(255, 255, 255))

    path = os.path.join(img_dir, "img_%02d.png" % (i + 1))
    img.save(path)
    print("Created: %s" % os.path.basename(path))

print("\nDone: 8 test images created in %s" % img_dir)