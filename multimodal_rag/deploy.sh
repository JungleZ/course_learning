#!/bin/bash
# 检测 python 命令
PY=$(command -v python3 || command -v python)
echo "Using: $PY"

echo "=== 1. 安装依赖 ==="
$PY -m pip install -r requirements.txt

echo "=== 2. 打 Gradio 补丁 ==="
$PY patch_gradio.py

echo "=== 3. 启动服务 ==="
nohup $PY src/app.py > app.log 2>&1 &
echo "PID: $!"
echo "日志: tail -f app.log"
echo "访问: http://公网IP:7861"
