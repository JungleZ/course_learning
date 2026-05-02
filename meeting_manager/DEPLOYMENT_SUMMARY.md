# Meeting Manager Linux 部署方案总结

## 📦 已创建的部署文件

### 核心部署脚本
1. **deploy_traditional.sh** - 传统部署脚本（推荐，无需 Docker）
   - 自动安装 Python 依赖
   - 配置 systemd 服务
   - 设置防火墙
   - 开机自启

2. **deploy.sh** - Docker 部署脚本（可选）
   - 自动安装 Docker
   - 构建镜像
   - 启动容器

### 配置文件
3. **requirements.txt** - Python 依赖清单
4. **gunicorn_config.py** - Gunicorn WSGI 服务器配置
5. **.env.example** - 环境变量示例
6. **Dockerfile** - Docker 镜像构建文件
7. **docker-compose.yml** - Docker Compose 编排配置
8. **nginx.conf.example** - Nginx 反向代理配置示例

### 文档
9. **DEPLOY_QUICK.md** - 快速开始指南
10. **DEPLOY_TRADITIONAL.md** - 传统部署详细教程
11. **DEPLOYMENT_OPTIONS.md** - 部署方式选择指南
12. **README_DEPLOY.md** - 完整部署文档（含 Docker、Nginx、HTTPS）

### 工具脚本
13. **package_for_deploy.bat** - Windows 打包脚本
14. **.gitignore** - Git 忽略配置

---

## 🎯 三种部署方式对比

### 方式一：传统部署 ⭐推荐新手
```bash
# 最简单，无需 Docker
sudo ./deploy_traditional.sh
```

**特点：**
- ✅ 简单快速
- ✅ 资源占用少
- ✅ 易于调试
- ❌ 环境隔离性较弱

**适合：** 个人项目、学习测试、单应用部署

---

### 方式二：Docker 部署
```bash
# 需要 Docker 环境
sudo ./deploy.sh
```

**特点：**
- ✅ 环境完全隔离
- ✅ 跨平台一致
- ✅ 易于迁移
- ❌ 需要学习 Docker

**适合：** 团队开发、多应用部署、微服务架构

---

### 方式三：Systemd 服务
```bash
# 传统部署已包含 systemd 配置
sudo ./deploy_traditional.sh
```

**特点：**
- ✅ 开机自启
- ✅ 自动重启
- ✅ 系统级管理
- ❌ 仅支持 Linux

**适合：** 生产环境、高可用性要求

---

## 🚀 快速开始

### Windows 用户
1. 双击运行 `package_for_deploy.bat`
2. 将生成的 `meeting-manager-deploy` 文件夹压缩
3. 上传到 Linux 服务器
4. SSH 登录服务器并解压
5. 运行 `sudo ./deploy_traditional.sh`

### Linux/Mac 用户
1. 直接上传整个 `meeting_manager` 目录
2. SSH 登录服务器
3. 运行 `sudo ./deploy_traditional.sh`

---

## 📋 部署后操作

### 访问应用
```
http://YOUR_SERVER_IP:8000
```

### 常用命令
```bash
# 查看状态
sudo systemctl status meeting-manager

# 查看日志
sudo journalctl -u meeting-manager -f

# 重启服务
sudo systemctl restart meeting-manager

# 备份数据库
cp /opt/meeting-manager/data/meeting.db /backup/backup_$(date +%Y%m%d).db
```

---

## 🔧 高级配置

### Nginx 反向代理
参考：[README_DEPLOY.md](README_DEPLOY.md#nginx-反向代理配置)

### HTTPS 配置
参考：[README_DEPLOY.md](README_DEPLOY.md#https-配置)

### 自动备份
参考：[DEPLOY_TRADITIONAL.md](DEPLOY_TRADITIONAL.md#自动备份脚本)

---

## ❓ 常见问题

### Q: 我应该选择哪种部署方式？
A: 
- 新手/个人 → 传统部署
- 团队/多应用 → Docker 部署
- 生产环境 → Systemd 服务

详见：[DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)

### Q: 可以从传统部署迁移到 Docker 吗？
A: 可以！备份数据后重新部署即可。

### Q: 如何更新应用？
A: 
```bash
cd /opt/meeting-manager
git pull  # 或上传新文件
sudo systemctl restart meeting-manager
```

### Q: 数据库在哪里？
A: `/opt/meeting-manager/data/meeting.db`

---

## 📚 文档导航

- **新手入门** → [DEPLOY_QUICK.md](DEPLOY_QUICK.md)
- **传统部署详解** → [DEPLOY_TRADITIONAL.md](DEPLOY_TRADITIONAL.md)
- **Docker 部署详解** → [README_DEPLOY.md](README_DEPLOY.md)
- **如何选择** → [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)

---

## 💡 最佳实践

1. **首次部署**：使用传统部署脚本，最简单
2. **生产环境**：配置 Nginx + HTTPS
3. **数据安全**：设置自动备份
4. **监控告警**：配置日志监控
5. **定期更新**：保持系统和依赖最新

---

## 🎉 祝您部署成功！

如有问题，请查阅对应文档或提交 Issue。
