# Meeting Manager 传统部署指南（无需 Docker）

## 🚀 快速开始（3 步完成）

### 第一步：准备服务器

确保您的 Linux 服务器已安装：
- Python 3.7+
- pip3
- sudo 权限

```bash
# 检查 Python
python3 --version

# 检查 pip
pip3 --version
```

### 第二步：上传代码

使用以下任一方式上传代码到服务器：

#### 方式 A：使用 scp（推荐）
```bash
# 从 Windows PowerShell
scp -r meeting_manager user@your-server-ip:/opt/

# 从 Linux/Mac
scp -r meeting_manager user@your-server-ip:/opt/
```

#### 方式 B：使用 Git
```bash
ssh user@your-server-ip
cd /opt
git clone <your-repo-url>
cd meeting_manager
```

#### 方式 C：使用 SFTP 工具
- WinSCP（Windows）
- FileZilla（跨平台）
- Cyberduck（Mac）

### 第三步：运行部署脚本

```bash
# SSH 登录服务器
ssh user@your-server-ip

# 进入部署目录
cd /opt/meeting_manager

# 赋予执行权限
chmod +x deploy_traditional.sh

# 运行部署（需要 sudo）
sudo ./deploy_traditional.sh
```

部署完成后，访问：`http://YOUR_SERVER_IP:8000`

---

## 📋 部署流程详解

部署脚本会自动完成以下步骤：

1. ✅ 检查并安装 Python 依赖
2. ✅ 创建部署目录 `/opt/meeting-manager`
3. ✅ 复制应用文件
4. ✅ 创建 Python 虚拟环境
5. ✅ 安装 Flask 和 Gunicorn
6. ✅ 生成安全密钥和配置文件
7. ✅ 配置 systemd 服务（开机自启）
8. ✅ 设置文件权限
9. ✅ 配置防火墙
10. ✅ 启动服务

---

## 🔧 手动部署（不使用脚本）

如果您想手动部署，请按以下步骤操作：

### 1. 创建部署目录
```bash
sudo mkdir -p /opt/meeting-manager/{data,logs,backup}
cd /opt/meeting-manager
```

### 2. 上传文件
将以下文件上传到 `/opt/meeting-manager`：
- `app.py`
- `requirements.txt`
- `gunicorn_config.py`
- `templates/` 目录
- `static/` 目录

### 3. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### 4. 创建环境变量文件
```bash
cat > .env << EOF
FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
APP_PORT=8000
DB_PATH=data/meeting.db
EOF
```

### 5. 配置 systemd 服务
```bash
sudo tee /etc/systemd/system/meeting-manager.service > /dev/null << 'EOF'
[Unit]
Description=Meeting Manager Flask Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/meeting-manager
EnvironmentFile=/opt/meeting-manager/.env
Environment="PATH=/opt/meeting-manager/venv/bin"
ExecStart=/opt/meeting-manager/venv/bin/gunicorn --config /opt/meeting-manager/gunicorn_config.py app:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### 6. 设置权限
```bash
sudo useradd -r -s /bin/false www-data 2>/dev/null || true
sudo chown -R www-data:www-data /opt/meeting-manager
sudo chmod 750 /opt/meeting-manager/data
```

### 7. 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable meeting-manager
sudo systemctl start meeting-manager
```

### 8. 开放防火墙端口
```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

## 📊 服务管理

### 查看服务状态
```bash
sudo systemctl status meeting-manager
```

### 查看日志
```bash
# systemd 日志
sudo journalctl -u meeting-manager -f

# 应用日志
tail -f /opt/meeting-manager/logs/app.log
tail -f /opt/meeting-manager/logs/error.log
```

### 重启服务
```bash
sudo systemctl restart meeting-manager
```

### 停止服务
```bash
sudo systemctl stop meeting-manager
```

### 禁用开机自启
```bash
sudo systemctl disable meeting-manager
```

---

## 🔄 更新应用

### 方法一：完整更新
```bash
# 1. 备份数据库
cp /opt/meeting-manager/data/meeting.db /opt/meeting-manager/backup/meeting_db_$(date +%Y%m%d).db

# 2. 停止服务
sudo systemctl stop meeting-manager

# 3. 上传新代码
scp -r * user@server:/opt/meeting-manager/

# 4. 更新依赖（如果有变化）
cd /opt/meeting-manager
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 5. 重启服务
sudo systemctl start meeting-manager
```

### 方法二：仅更新代码（推荐）
```bash
# 如果使用 Git
cd /opt/meeting-manager
git pull
sudo systemctl restart meeting-manager
```

---

## 💾 备份与恢复

### 手动备份
```bash
# 备份数据库
cp /opt/meeting-manager/data/meeting.db /backup/meeting_db_$(date +%Y%m%d_%H%M%S).db

# 备份整个应用
tar czf /backup/meeting-manager_$(date +%Y%m%d).tar.gz /opt/meeting-manager/
```

### 自动备份脚本
创建 `/opt/meeting-manager/backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/opt/meeting-manager/backup"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/opt/meeting-manager/data/meeting.db"

mkdir -p ${BACKUP_DIR}

# 备份数据库
cp ${DB_FILE} ${BACKUP_DIR}/meeting_db_${DATE}.db

# 删除7天前的备份
find ${BACKUP_DIR} -name "meeting_db_*.db" -mtime +7 -delete

echo "Backup completed: ${DATE}"
```

设置定时任务：
```bash
chmod +x /opt/meeting-manager/backup.sh

# 编辑 crontab
sudo crontab -e

# 添加每天凌晨3点备份
0 3 * * * /opt/meeting-manager/backup.sh >> /opt/meeting-manager/logs/backup.log 2>&1
```

### 恢复数据
```bash
# 1. 停止服务
sudo systemctl stop meeting-manager

# 2. 恢复数据库
cp /backup/meeting_db_20240101.db /opt/meeting-manager/data/meeting.db

# 3. 设置权限
sudo chown www-data:www-data /opt/meeting-manager/data/meeting.db

# 4. 启动服务
sudo systemctl start meeting-manager
```

---

## 🔒 安全加固

### 1. 修改默认端口
编辑 `.env` 文件：
```env
APP_PORT=8888  # 改为其他端口
```

重启服务：
```bash
sudo systemctl restart meeting-manager
```

### 2. 配置 Nginx 反向代理
参见 [README_DEPLOY.md](README_DEPLOY.md#nginx-反向代理配置)

### 3. 启用 HTTPS
参见 [README_DEPLOY.md](README_DEPLOY.md#https-配置)

### 4. 限制访问 IP
在 Nginx 配置中添加：
```nginx
location / {
    allow 192.168.1.0/24;  # 只允许内网访问
    deny all;
    proxy_pass http://127.0.0.1:8000;
}
```

---

## ❓ 故障排查

### 问题 1：服务无法启动
```bash
# 查看详细错误
sudo journalctl -u meeting-manager -n 50 --no-pager

# 常见原因：
# - 端口被占用：lsof -i :8000
# - 权限问题：ls -la /opt/meeting-manager/data
# - 依赖缺失：source venv/bin/activate && pip list
```

### 问题 2：502 Bad Gateway
```bash
# 检查 Gunicorn 是否运行
ps aux | grep gunicorn

# 检查端口监听
sudo lsof -i :8000

# 重启服务
sudo systemctl restart meeting-manager
```

### 问题 3：数据库锁定
```bash
# 停止服务
sudo systemctl stop meeting-manager

# 删除锁文件
rm -f /opt/meeting-manager/data/meeting.db-shm
rm -f /opt/meeting-manager/data/meeting.db-wal

# 重启服务
sudo systemctl start meeting-manager
```

### 问题 4：权限错误
```bash
# 修复权限
sudo chown -R www-data:www-data /opt/meeting-manager
sudo chmod 750 /opt/meeting-manager/data
```

### 问题 5：内存不足
```bash
# 查看内存使用
free -h

# 调整 Gunicorn 工作进程数
sudo vim /opt/meeting-manager/gunicorn_config.py
# workers = 2  # 减少工作进程数

sudo systemctl restart meeting-manager
```

---

## 📈 性能优化

### 1. 调整 Gunicorn 配置
编辑 `gunicorn_config.py`：

```python
# 根据服务器配置调整
workers = 4  # CPU 核心数 * 2 + 1
threads = 2
max_requests = 1000
timeout = 120
```

### 2. 启用缓存
安装 Redis（可选）：
```bash
sudo apt install redis-server
pip install flask-caching
```

### 3. 静态文件优化
使用 Nginx 提供静态文件（见 Nginx 配置示例）

---

## 🎯 下一步

- [ ] 配置 Nginx 反向代理
- [ ] 启用 HTTPS（Let's Encrypt）
- [ ] 设置自动备份
- [ ] 配置监控告警
- [ ] 设置日志轮转

详细配置请参考 [README_DEPLOY.md](README_DEPLOY.md)

---

## 📞 获取帮助

遇到问题？
1. 查看日志：`sudo journalctl -u meeting-manager -f`
2. 检查状态：`sudo systemctl status meeting-manager`
3. 查阅文档：[DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)
