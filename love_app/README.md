# Love App - 恋爱观与情商小贴士

这是一个基于Flask的Web应用，提供恋爱观和情商相关的语录和建议。

## ⚠️ 重要说明

**本项目不能使用 `python -m http.server` 部署！**

### 为什么？
- 这是一个 **Flask Web应用**，需要Flask框架支持
- 使用了Jinja2模板引擎进行服务端渲染
- 包含后端API端点（`/api/quote`）
- 需要Python后端处理动态内容

## 项目结构

```
love_app/
├── app.py              # Flask主应用
├── deploy.py           # 部署脚本
├── requirements.txt    # Python依赖
├── start_server.bat    # Windows启动脚本（新增）
├── templates/
│   └── index.html      # HTML模板
└── static/
    ├── css/
    │   └── style.css   # 样式文件
    └── js/
        └── script.js   # JavaScript文件
```

## 如何运行

### 方法1：使用启动脚本（推荐）
双击 `start_server.bat` 文件即可自动安装依赖并启动服务器。

### 方法2：手动启动

#### 步骤1：安装依赖
```bash
C:\Users\v-jaggerzhang\.conda\envs\PythonProject1\python.exe -m pip install Flask==2.3.3
```

#### 步骤2：启动应用
```bash
cd love_app
C:\Users\v-jaggerzhang\.conda\envs\PythonProject1\python.exe app.py
```

### 方法3：使用deploy.py
```bash
cd love_app
C:\Users\v-jaggerzhang\.conda\envs\PythonProject1\python.exe deploy.py
```

## 访问应用

启动后在浏览器中访问：
```
http://localhost:5000
```

## 功能特点

- 📝 随机显示恋爱观和情商相关的语录
- 🔄 每隔几秒自动更新语录
- 💡 提供情感智慧和人际关系建议
- 🎨 简洁美观的用户界面

## 技术栈

- **后端**: Flask 2.3.3
- **前端**: HTML5, CSS3, JavaScript
- **模板引擎**: Jinja2
- **Python版本**: 3.10+

## API端点

- `GET /` - 主页
- `GET /api/quote` - 获取随机语录（返回JSON格式）

## 注意事项

- 默认运行在端口 5000
- 开发模式下启用了debug模式
- 生产环境建议使用Gunicorn等WSGI服务器
