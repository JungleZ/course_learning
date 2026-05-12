# Day 8：Docker 容器化部署

## 🎯 今日目标
1. 理解 Docker 的核心概念
2. 学会编写 Dockerfile
3. 用 Docker 容器化部署 ML 模型
4. 学习 docker-compose 编排多服务

---

## 🤔 为什么需要 Docker？

| 没有 Docker | 有 Docker |
|------------|-----------|
| "在我电脑上能跑！" | 到处都能跑 ✅ |
| 依赖版本冲突 | 环境完全隔离 ✅ |
| 部署配置复杂 | 一条命令部署 ✅ |
| 扩容困难 | 弹性扩容 ✅ |

**Docker = 把应用+环境一起打包，确保在任何地方都能运行！**

---

## 🔑 Docker 核心概念

| 概念 | 解释 | 类比 |
|------|------|------|
| **镜像 (Image)** | 应用的打包模板 | 菜谱 |
| **容器 (Container)** | 镜像的运行实例 | 按菜谱做的菜 |
| **Dockerfile** | 构建镜像的脚本 | 写菜谱的过程 |
| **Registry** | 镜像仓库 | 菜谱图书馆 |

### 工作流程：
```
编写 Dockerfile → 构建镜像 → 运行容器 → 推送到仓库
```

---

## 📁 项目结构

```
day08-docker/
├── guide.md           # 本文件
├── app.py             # Flask API 应用
├── Dockerfile         # Docker 镜像构建脚本
├── requirements.txt   # Python 依赖
├── docker-compose.yml # 多服务编排
└── .dockerignore      # Docker 忽略文件
```

---

## 🚀 运行步骤

### 第1步：安装 Docker

#### Windows：
1. 下载 Docker Desktop：https://www.docker.com/products/docker-desktop
2. 安装并启动 Docker Desktop
3. 验证：
```bash
docker --version
docker run hello-world
```

#### 注意：Windows 需要开启 WSL2 或 Hyper-V

### 第2步：构建 Docker 镜像
```bash
cd day08-docker
docker build -t iris-classifier:v1 .
```

- `-t` 给镜像打标签（名字:版本）
- `.` 表示 Dockerfile 在当前目录

### 第3步：运行 Docker 容器
```bash
docker run -d -p 5000:5000 --name iris-app iris-classifier:v1
```

- `-d` 后台运行
- `-p 5000:5000` 端口映射（主机:容器）
- `--name` 给容器起名字

### 第4步：测试 API
```bash
curl http://127.0.0.1:5000/health
curl -X POST http://127.0.0.1:5000/predict -H "Content-Type: application/json" -d "{\"features\": [5.1, 3.5, 1.4, 0.2]}"
```

### 第5步：管理容器
```bash
# 查看运行中的容器
docker ps

# 查看日志
docker logs iris-app

# 停止容器
docker stop iris-app

# 启动已停止的容器
docker start iris-app

# 删除容器
docker rm iris-app

# 删除镜像
docker rmi iris-classifier:v1
```

---

## 📝 Dockerfile 详解

```dockerfile
# 基础镜像 - Python 3.9 精简版
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装（利用缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### 优化技巧：
1. **利用缓存层**：先复制 requirements.txt 并安装依赖，再复制代码
2. **使用精简镜像**：`python:3.9-slim` 比 `python:3.9` 小很多
3. **不缓存 pip**：`--no-cache-dir` 减小镜像大小
4. **生产级服务器**：用 gunicorn 替代 Flask 开发服务器

---

## 🐙 docker-compose 编排

当需要多个服务（如 API + 数据库）时，用 docker-compose：

```bash
docker-compose up -d     # 启动所有服务
docker-compose down       # 停止所有服务
docker-compose logs -f    # 查看日志
```

---

## ⚠️ 常见问题

### Q: Docker 构建很慢
A: 使用国内镜像源，配置 Docker 镜像加速器

### Q: 容器内无法访问外网
A: 检查 Docker 网络配置，尝试 `--network host`

### Q: Windows 上 Docker 很卡
A: 确保开启了 WSL2，在 Docker Desktop 设置中分配足够内存

---

## ✅ 今日检查清单
- [ ] Docker 安装成功，`docker --version` 正常
- [ ] 成功构建 Docker 镜像
- [ ] 成功运行容器并测试 API
- [ ] 理解 Dockerfile 各行含义
- [ ] 了解 docker-compose 的作用

## 🎉 完成 Day 8！明天学习云服务器部署。
