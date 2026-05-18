#!/bin/bash
# 部署脚本 - 阿里云服务器

echo "=== 1. 安装依赖 ==="
pip install -r requirements.txt

echo "=== 2. 打 Gradio 补丁 ==="
python patch_gradio.py

echo "=== 3. 启动服务 ==="
nohup python src/app.py > app.log 2>&1 &
echo "PID: $!"
echo "日志: tail -f app.log"
echo "访问: http://公网IP:7861"