#!/bin/bash

# Meeting Manager Linux 部署脚本 - 传统方式（无需 Docker）
# 使用方法: chmod +x deploy_traditional.sh && sudo ./deploy_traditional.sh

set -e

echo "========================================="
echo "Meeting Manager 传统部署脚本（无 Docker）"
echo "========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
APP_NAME="meeting-manager"
APP_PORT=${APP_PORT:-8000}
DEPLOY_DIR="/opt/${APP_NAME}"
PYTHON_VERSION="python3"

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 函数：打印信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 步骤 1：检查系统依赖
check_dependencies() {
    print_step "检查系统依赖..."
    
    # 检查 Python
    if ! command -v ${PYTHON_VERSION} &> /dev/null; then
        print_warning "Python3 未安装，正在安装..."
        if command -v apt-get &> /dev/null; then
            apt-get update && apt-get install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            yum install -y python3 python3-pip
        fi
    fi
    
    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        print_warning "pip3 未安装，正在安装..."
        if command -v apt-get &> /dev/null; then
            apt-get install -y python3-pip
        elif command -v yum &> /dev/null; then
            yum install -y python3-pip
        fi
    fi
    
    # 检查 git（可选，用于更新代码）
    if ! command -v git &> /dev/null; then
        print_warning "Git 未安装（可选），建议安装以便后续更新"
    fi
    
    print_info "依赖检查完成"
    print_info "Python 版本: $(${PYTHON_VERSION} --version)"
    print_info "Pip 版本: $(pip3 --version)"
}

# 步骤 2：创建部署目录
create_deploy_dir() {
    print_step "创建部署目录..."
    mkdir -p ${DEPLOY_DIR}
    mkdir -p ${DEPLOY_DIR}/data
    mkdir -p ${DEPLOY_DIR}/logs
    mkdir -p ${DEPLOY_DIR}/backup
    
    print_info "部署目录创建完成: ${DEPLOY_DIR}"
}

# 步骤 3：复制应用文件
copy_files() {
    print_step "复制应用文件..."
    
    # 如果当前目录有文件，则复制
    if [ -f "app.py" ]; then
        cp -r * ${DEPLOY_DIR}/ 2>/dev/null || true
        cp .env.example ${DEPLOY_DIR}/.env 2>/dev/null || true
        print_info "文件复制完成"
    else
        print_warning "当前目录没有应用文件，请手动上传到 ${DEPLOY_DIR}"
    fi
}

# 步骤 4：设置 Python 虚拟环境
setup_venv() {
    print_step "设置 Python 虚拟环境..."
    
    cd ${DEPLOY_DIR}
    
    # 创建虚拟环境
    ${PYTHON_VERSION} -m venv venv
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_info "Python 依赖安装完成"
    else
        print_error "requirements.txt 不存在"
        exit 1
    fi
    
    # 退出虚拟环境
    deactivate
    
    print_info "虚拟环境设置完成"
}

# 步骤 5：生成环境变量
generate_env() {
    print_step "生成环境变量配置..."
    
    cd ${DEPLOY_DIR}
    
    if [ ! -f .env ]; then
        # 生成随机密钥
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
        
        cat > .env << EOF
# Meeting Manager 环境配置
FLASK_SECRET_KEY=${SECRET_KEY}
APP_PORT=${APP_PORT}
DB_PATH=data/meeting.db
EOF
        
        print_info "已生成 .env 文件"
        print_warning "请根据实际情况修改 ${DEPLOY_DIR}/.env 文件"
    else
        print_info ".env 文件已存在"
    fi
}

# 步骤 6：配置 systemd 服务
setup_systemd() {
    print_step "配置 systemd 服务..."
    
    cat > /etc/systemd/system/${APP_NAME}.service << EOF
[Unit]
Description=Meeting Manager Flask Application
After=network.target
Wants=network-online.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=${DEPLOY_DIR}
EnvironmentFile=${DEPLOY_DIR}/.env
Environment="PATH=${DEPLOY_DIR}/venv/bin"
ExecStart=${DEPLOY_DIR}/venv/bin/gunicorn --config ${DEPLOY_DIR}/gunicorn_config.py app:app
Restart=on-failure
RestartSec=10
StandardOutput=append:${DEPLOY_DIR}/logs/app.log
StandardError=append:${DEPLOY_DIR}/logs/error.log

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=${DEPLOY_DIR}/data

[Install]
WantedBy=multi-user.target
EOF
    
    # 重载 systemd
    systemctl daemon-reload
    
    # 启用开机自启
    systemctl enable ${APP_NAME}
    
    print_info "systemd 服务配置完成"
}

# 步骤 7：设置权限
set_permissions() {
    print_step "设置文件权限..."
    
    # 创建 www-data 用户（如果不存在）
    id -u www-data &>/dev/null || useradd -r -s /bin/false www-data
    
    # 设置所有者
    chown -R www-data:www-data ${DEPLOY_DIR}
    
    # 设置目录权限
    chmod 755 ${DEPLOY_DIR}
    chmod 750 ${DEPLOY_DIR}/data
    chmod 640 ${DEPLOY_DIR}/.env
    
    # 设置日志文件权限
    touch ${DEPLOY_DIR}/logs/app.log ${DEPLOY_DIR}/logs/error.log
    chown www-data:www-data ${DEPLOY_DIR}/logs/*.log
    chmod 644 ${DEPLOY_DIR}/logs/*.log
    
    print_info "权限设置完成"
}

# 步骤 8：配置防火墙
configure_firewall() {
    print_step "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        ufw allow ${APP_PORT}/tcp
        print_info "UFW: 已开放端口 ${APP_PORT}"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=${APP_PORT}/tcp
        firewall-cmd --reload
        print_info "Firewalld: 已开放端口 ${APP_PORT}"
    else
        print_warning "未检测到防火墙工具，请手动开放端口 ${APP_PORT}"
    fi
}

# 步骤 9：启动服务
start_service() {
    print_step "启动服务..."
    
    systemctl start ${APP_NAME}
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if systemctl is-active --quiet ${APP_NAME}; then
        print_info "服务启动成功！"
    else
        print_error "服务启动失败"
        print_error "查看日志: journalctl -u ${APP_NAME} -f"
        exit 1
    fi
}

# 步骤 10：显示部署信息
show_info() {
    echo ""
    echo "========================================="
    echo -e "${GREEN}✓ 部署完成！${NC}"
    echo "========================================="
    echo ""
    echo "访问地址: http://YOUR_SERVER_IP:${APP_PORT}"
    echo ""
    echo "部署目录: ${DEPLOY_DIR}"
    echo "数据库位置: ${DEPLOY_DIR}/data/meeting.db"
    echo "日志文件: ${DEPLOY_DIR}/logs/"
    echo ""
    echo "常用命令:"
    echo "  查看状态: sudo systemctl status ${APP_NAME}"
    echo "  查看日志: sudo journalctl -u ${APP_NAME} -f"
    echo "  重启服务: sudo systemctl restart ${APP_NAME}"
    echo "  停止服务: sudo systemctl stop ${APP_NAME}"
    echo "  查看实时日志: tail -f ${DEPLOY_DIR}/logs/app.log"
    echo ""
    echo "更新应用:"
    echo "  1. 上传新代码到 ${DEPLOY_DIR}"
    echo "  2. sudo systemctl restart ${APP_NAME}"
    echo ""
    echo "备份数据库:"
    echo "  cp ${DEPLOY_DIR}/data/meeting.db ${DEPLOY_DIR}/backup/meeting_db_\$(date +%Y%m%d).db"
    echo ""
    echo "========================================="
}

# 主流程
main() {
    check_dependencies
    create_deploy_dir
    copy_files
    setup_venv
    generate_env
    setup_systemd
    set_permissions
    configure_firewall
    start_service
    show_info
}

# 执行主流程
main
