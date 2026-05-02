# Meeting Manager - Linux 服务器部署指南

## 🎯 选择您的部署方式

我们提供 **3 种部署方式**，请根据您的需求和经验选择：

| 部署方式 | 适合人群 | 难度 | 特点 |
|---------|---------|------|------|
| **[传统部署](DEPLOY_TRADITIONAL.md)** ⭐推荐 | 新手/个人项目 | ⭐⭐ | 简单快速，无需 Docker |
| **[Docker 部署](README_DEPLOY.md)** | 团队/多应用 | ⭐⭐⭐ | 环境隔离，易于迁移 |
| **[Systemd 服务](DEPLOY_TRADITIONAL.md)** | 生产环境 | ⭐⭐ | 开机自启，自动恢复 |

> 💡 **不确定选哪个？** 从**传统部署**开始，最简单！

---

## 🚀 快速开始（传统部署 - 推荐）

### 第一步：上传文件到服务器

```bash
# Windows PowerShell
scp -r meeting_manager user@your-server-ip:/opt/

# 或使用 WinSCP、FileZilla 等图形化工具
```

### 第二步：运行部署脚本

```bash
# SSH 登录服务器
ssh user@your-server-ip

# 进入目录并运行
cd /opt/meeting_manager
chmod +x deploy_traditional.sh
sudo ./deploy_traditional.sh
```

### 第三步：访问应用

打开浏览器访问：`http://YOUR_SERVER_IP:8000`

✅ 完成！就是这么简单！

---

## 📋 其他部署方式

### Docker 部署
适合有 Docker 经验的用户，查看 [README_DEPLOY.md](README_DEPLOY.md)

### 手动部署
想完全控制每个步骤？查看 [DEPLOY_TRADITIONAL.md](DEPLOY_TRADITIONAL.md#手动部署不使用脚本)

---

## 🔧 常用操作

### 查看服务状态
```bash
sudo systemctl status meeting-manager
```

### 查看日志
```bash
sudo journalctl -u meeting-manager -f
```

### 重启服务
```bash
sudo systemctl restart meeting-manager
```

### 备份数据库
```bash
cp /opt/meeting-manager/data/meeting.db /backup/meeting_db_$(date +%Y%m%d).db
```

### 更新应用
```bash
cd /opt/meeting-manager
git pull  # 如果使用 Git
sudo systemctl restart meeting-manager
```

---

## 📚 详细文档

- **[部署方式选择指南](DEPLOYMENT_OPTIONS.md)** - 帮助选择合适的部署方式
- **[传统部署详解](DEPLOY_TRADITIONAL.md)** - 完整的传统部署教程
- **[Docker 部署详解](README_DEPLOY.md)** - Docker 和高级配置
- **[常见问题解答](README_DEPLOY.md#常见问题)** - 遇到问题先查这里

---

## ❓ 需要帮助？

1. **选择困难？** → 阅读 [部署方式选择指南](DEPLOYMENT_OPTIONS.md)
2. **部署失败？** → 查看日志 `sudo journalctl -u meeting-manager -f`
3. **功能问题？** → 查阅 [常见问题](README_DEPLOY.md#常见问题)

---

## 🎉 祝您部署顺利！
