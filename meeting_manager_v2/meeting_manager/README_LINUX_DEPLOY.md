# Meeting Manager - Linux 服务器部署指南

## 🚀 极简部署（推荐！3 步完成）

### ⭐ 方法一：一键脚本（最简单）

```bash
# 1. 上传到服务器
scp -r meeting_manager user@server:/tmp/

# 2. SSH 登录并运行
ssh user@server
cd /tmp/meeting_manager
chmod +x deploy_simple.sh
./deploy_simple.sh
```

**完成！** 访问 `http://YOUR_SERVER_IP:8000`

详细文档：[DEPLOY_SIMPLE.md](DEPLOY_SIMPLE.md)

---

### ⚡ 方法二：3 条命令（无需脚本）

```bash
pip3 install flask gunicorn
export FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
nohup gunicorn --bind 0.0.0.0:8000 --workers 2 app:app &
```

**完成！** 就这么简单！

---

## 📦 其他部署方式

如果您需要更高级的功能（开机自启、自动重启、Docker 隔离等），可以选择：

| 部署方式 | 适合人群 | 特点 |
|---------|---------|------|
| **[极简部署](DEPLOY_SIMPLE.md)** ⭐ | **所有人** | **最简单，3 步完成** |
| [传统部署](DEPLOY_TRADITIONAL.md) | 生产环境 | systemd 管理，开机自启 |
| [Docker 部署](README_DEPLOY.md) | 团队开发 | 环境隔离，易于迁移 |

> 💡 **建议**：先用**极简部署**快速体验，需要更多功能时再升级到其他方案。

---

## 🔧 常用操作

```bash
# 查看是否运行
ps aux | grep gunicorn

# 查看日志
tail -f /opt/meeting-manager/logs.txt

# 停止服务
pkill -f gunicorn

# 重启服务
pkill -f gunicorn && cd /opt/meeting-manager && nohup gunicorn --bind 0.0.0.0:8000 --workers 2 app:app > logs.txt 2>&1 &
```

---

## 📚 完整文档

- **[极简部署指南](DEPLOY_SIMPLE.md)** - 超简单的 3 步部署
- [传统部署详解](DEPLOY_TRADITIONAL.md) - systemd 服务管理
- [Docker 部署详解](README_DEPLOY.md) - 容器化部署
- [部署方式对比](DEPLOYMENT_OPTIONS.md) - 如何选择

---

## ❓ 常见问题

### Q: 我需要 Docker 吗？
A: **不需要！** 极简部署只需 Python3，无需 Docker。

### Q: 如何修改端口？
A: `./deploy_simple.sh 9000` 或使用 `--bind 0.0.0.0:9000`

### Q: 服务器重启后怎么办？
A: 重新运行启动命令即可，或使用传统部署（支持开机自启）。

### Q: 数据库在哪里？
A: `/opt/meeting-manager/data/meeting.db`

---

## 🎉 开始使用吧！

选择最适合您的方式，开始部署！
