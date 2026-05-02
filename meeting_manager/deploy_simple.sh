#!/bin/bash

# Meeting Manager 极简部署脚本
# 使用方法: chmod +x deploy_simple.sh && ./deploy_simple.sh

set -e

echo "========================================="
echo "Meeting Manager 极简部署"
echo "========================================="
echo ""

# 配置
APP_DIR="/opt/meeting-manager"
PORT=${1:-8000}  # 支持命令行指定端口，默认 8000

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "[1/5] 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3${NC}"
    echo "请先安装: sudo apt install python3 python3-pip"
    exit 1
fi
echo "✓ Python3 已安装"

echo ""
echo "[2/5] 创建目录..."
mkdir -p $APP_DIR
echo "✓ 目录创建完成: $APP_DIR"

echo ""
echo "[3/5] 复制文件..."
if [ -f "app.py" ]; then
    cp -r * $APP_DIR/ 2>/dev/null || true
    echo "✓ 文件复制完成"
else
    echo -e "${RED}错误: 当前目录没有 app.py${NC}"
    echo "请先进入 meeting_manager 目录"
    exit 1
fi

echo ""
echo "[4/5] 安装依赖..."
cd $APP_DIR
pip3 install flask gunicorn > /dev/null 2>&1 || pip install flask gunicorn > /dev/null 2>&1
echo "✓ 依赖安装完成"

echo ""
echo "[5/5] 启动服务..."

# 生成密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)

# 后台启动
nohup bash -c "cd $APP_DIR && FLASK_SECRET_KEY=$SECRET_KEY gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app > logs.txt 2>&1" &

sleep 2

# 检查是否启动成功
if ps aux | grep "[g]unicorn" > /dev/null; then
    echo -e "${GREEN}✓ 部署成功！${NC}"
    echo ""
    echo "访问地址: http://YOUR_SERVER_IP:$PORT"
    echo ""
    echo "常用命令:"
    echo "  查看进程: ps aux | grep gunicorn"
    echo "  查看日志: tail -f $APP_DIR/logs.txt"
    echo "  停止服务: pkill -f gunicorn"
    echo ""
else
    echo -e "${RED}✗ 启动失败，请查看日志:${NC}"
    cat $APP_DIR/logs.txt
    exit 1
fi
