# Meeting Manager 极简部署指南

## 🚀 超简单！3 步完成部署

### 方法一：一键脚本（最简单）⭐

```bash
# 1. 上传文件到服务器
scp -r meeting_manager user@server:/tmp/

# 2. SSH 登录并运行
ssh user@server
cd /tmp/meeting_manager
chmod +x deploy_simple.sh
./deploy_simple.sh
```

**就这么简单！** 访问 `http://YOUR_SERVER_IP:8000`

---

### 方法二：手动 3 命令（无需脚本）

```bash
# 1. 安装依赖
pip3 install flask gunicorn

# 2. 生成密钥并启动
export FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
nohup gunicorn --bind 0.0.0.0:8000 --workers 2 app:app &

# 3. 完成！
```

访问 `http://YOUR_SERVER_IP:8000`

---

### 方法三：直接运行（最快，适合测试）

```bash
# 1. 安装 Flask
pip3 install flask

# 2. 直接运行
python3 app.py
```

访问 `http://YOUR_SERVER_IP:5000`

> ⚠️ 这种方式仅适合测试，不适合生产环境

---

## 📋 对比

| 方式 | 难度 | 适用场景 | 持久化 |
|------|------|---------|--------|
| **一键脚本** | ⭐ | 快速部署 | ✅ 后台运行 |
| **3 命令** | ⭐⭐ | 学习理解 | ✅ 后台运行 |
| **直接运行** | ⭐ | 临时测试 | ❌ 关闭终端即停 |

---

## 🔧 常用操作

### 查看是否运行
```bash
ps aux | grep gunicorn
```

### 查看日志
```bash
tail -f /opt/meeting-manager/logs.txt
```

### 停止服务
```bash
pkill -f gunicorn
```

### 重启服务
```bash
pkill -f gunicorn
cd /opt/meeting-manager
nohup gunicorn --bind 0.0.0.0:8000 --workers 2 app:app > logs.txt 2>&1 &
```

### 修改端口
```bash
# 停止当前服务
pkill -f gunicorn

# 指定新端口启动
cd /opt/meeting-manager
nohup gunicorn --bind 0.0.0.0:9000 --workers 2 app:app > logs.txt 2>&1 &
```

---

## 💡 提示

- **默认端口**: 8000
- **自定义端口**: `./deploy_simple.sh 9000`
- **数据位置**: `/opt/meeting-manager/data/meeting.db`
- **日志位置**: `/opt/meeting-manager/logs.txt`

---

## ❓ 遇到问题？

### Python3 未安装
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

### 端口被占用
```bash
# 查看谁在使用 8000 端口
lsof -i :8000

# 使用其他端口
./deploy_simple.sh 9000
```

### 权限问题
```bash
# 赋予执行权限
chmod +x deploy_simple.sh

# 或使用 sudo
sudo ./deploy_simple.sh
```

---

## 🎉 就这么简单！

不需要 Docker、不需要 systemd、不需要复杂配置。
**3 条命令，搞定部署！**
