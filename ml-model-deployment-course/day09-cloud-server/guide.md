# Day 9：云服务器部署（阿里云/腾讯云）

## 🎯 今日目标
1. 学习购买和配置云服务器
2. 在云服务器上部署 ML 模型
3. 配置 Nginx 反向代理
4. 使用 systemd 管理服务

---

## 🖥️ 什么是云服务器？

云服务器 = 别人帮你管的一台远程电脑，你通过网络使用它。

| 优点 | 说明 |
|------|------|
| 7x24 运行 | 不怕断电关机 |
| 公网 IP | 任何人都可访问 |
| 弹性扩容 | 随时升级配置 |
| 便宜 | 最低几十元/月 |

---

## 📋 第一步：购买云服务器

### 阿里云 ECS

1. 访问 https://www.aliyun.com/product/ecs
2. 选择配置：
   - **CPU/内存**：2核4G（足够跑小模型）
   - **系统**：Ubuntu 22.04 LTS（推荐）
   - **带宽**：1-5Mbps
   - **硬盘**：40G SSD
3. 付费方式：按量付费（灵活）或包年包月（便宜）

### 腾讯云 CVM

1. 访问 https://cloud.tencent.com/product/cvm
2. 配置类似，选 Ubuntu 22.04

### 💰 新用户优惠
- 阿里云：新用户通常有首年 99 元特惠
- 腾讯云：新用户也有类似优惠
- AWS：有免费套餐（12个月免费 t2.micro）

---

## 📋 第二步：连接服务器

### 获取连接信息
购买后会得到：
- **公网 IP**：如 `47.100.200.300`
- **用户名**：通常 `root`
- **密码/密钥**：购买时设置

### SSH 连接

```bash
# Windows 用户可以用 PowerShell 或 Git Bash
ssh root@你的公网IP

# 如果使用密钥
ssh -i 你的密钥.pem root@你的公网IP
```

### Windows 没有 SSH？
- 用 **PuTTY**：https://www.putty.org/
- 或用 **MobaXterm**：https://mobaxterm.mobatek.net/

---

## 📋 第三步：服务器环境配置

连接上服务器后，**按顺序执行**：

```bash
# 1. 更新系统
apt update && apt upgrade -y

# 2. 安装 Python 3 和 pip
apt install python3 python3-pip python3-venv -y

# 3. 创建项目目录
mkdir -p /opt/ml-app
cd /opt/ml-app

# 4. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 5. 上传代码（在本地电脑执行）
# 方式1：用 scp
scp -r ./day08-docker/* root@你的IP:/opt/ml-app/

# 方式2：用 git
apt install git -y
git clone 你的仓库地址 /opt/ml-app

# 6. 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 7. 安装 gunicorn
pip install gunicorn
```

---

## 📋 第四步：启动模型服务

### 方式1：直接启动（测试用）
```bash
cd /opt/ml-app
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 方式2：systemd 服务（推荐，生产用）

创建服务文件：
```bash
cat > /etc/systemd/system/ml-api.service << 'EOF'
[Unit]
Description=ML Model API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ml-app
ExecStart=/opt/ml-app/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

启动服务：
```bash
# 重载配置
systemctl daemon-reload

# 启动服务
systemctl start ml-api

# 设置开机自启
systemctl enable ml-api

# 查看状态
systemctl status ml-api

# 查看日志
journalctl -u ml-api -f
```

---

## 📋 第五步：配置 Nginx 反向代理

```bash
# 安装 Nginx
apt install nginx -y

# 创建配置
cat > /etc/nginx/sites-available/ml-api << 'EOF'
server {
    listen 80;
    server_name 你的域名或IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/ml-api /etc/nginx/sites-enabled/
nginx -t          # 测试配置
systemctl restart nginx
```

---

## 📋 第六步：开放端口

### 阿里云
1. 进入 ECS 控制台
2. 找到安全组
3. 添加规则：开放 80 端口（HTTP）

### 腾讯云
1. 进入 CVM 控制台
2. 安全组 → 添加规则
3. 开放 80 端口

### 验证
```bash
curl http://你的公网IP/health
```

---

## 🔒 安全加固

```bash
# 1. 创建普通用户（不用 root）
adduser mluser
usermod -aG sudo mluser

# 2. 禁用密码登录，只用密钥
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# 3. 配置防火墙
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable

# 4. 安装 SSL 证书（用 Let's Encrypt）
apt install certbot python3-certbot-nginx -y
certbot --nginx -d 你的域名
```

---

## 📊 完整部署架构

```
          互联网用户
              │
              ↓
    ┌─────────────────┐
    │  云服务器 (ECS)   │
    │                  │
    │  ┌────────────┐  │
    │  │   Nginx    │  │ ← 端口80，反向代理
    │  │  :80       │  │
    │  └─────┬──────┘  │
    │        │         │
    │  ┌─────↓──────┐  │
    │  │  Gunicorn  │  │ ← 端口5000，WSGI服务
    │  │  :5000     │  │
    │  └─────┬──────┘  │
    │        │         │
    │  ┌─────↓──────┐  │
    │  │  Flask App │  │ ← ML模型推理
    │  │ + Model    │  │
    │  └────────────┘  │
    └─────────────────┘
```

---

## ✅ 今日检查清单
- [ ] 成功购买并连接云服务器
- [ ] 在服务器上安装 Python 和依赖
- [ ] 成功启动模型 API 服务
- [ ] 配置 Nginx 反向代理
- [ ] 通过公网 IP 访问 API
- [ ] 了解基本安全加固措施

## 🎉 完成 Day 9！明天学习 HuggingFace Spaces 部署。
