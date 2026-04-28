# DISC领导力测试应用

这是一个基于DISC模型的领导力风格测试Web应用，包含24道测试题。

## 项目结构

```
disc_leadership_test/
├── index.html          # 主页面
├── start_server.bat    # Windows启动脚本
├── css/
│   └── style.css       # 样式文件
├── js/
│   └── app.js          # JavaScript逻辑
└── README.md           # 说明文档
```

## 如何运行

### 方法1：使用批处理脚本（推荐）
双击 `start_server.bat` 文件即可启动服务器。

### 方法2：手动启动
在命令行中执行：
```bash
cd disc_leadership_test
C:\Users\v-jaggerzhang\.conda\envs\PythonProject1\python.exe -m http.server 8088
```

## 访问应用

启动服务器后，在浏览器中访问：
```
http://localhost:8088
```

## 功能特点

- ✅ 24道DISC领导力测试题
- ✅ 实时计算D/I/S/C四个维度得分
- ✅ 可视化柱状图展示结果
- ✅ 详细的领导风格分析和建议
- ✅ 响应式设计，支持移动端
- ✅ 纯前端实现，无需后端

## DISC模型说明

- **D (Dominance) 支配型**: 果断、目标导向、执行力强
- **I (Influence) 影响型**: 热情、善于沟通、鼓舞他人
- **S (Steadiness) 稳健型**: 稳定、可靠、重视和谐
- **C (Compliance) 谨慎型**: 精确、系统、注重质量

## 注意事项

- 服务器运行在端口 8088，避免与已有的 8089 端口冲突
- 按 Ctrl+C 可以停止服务器
- 所有数据仅在本地处理，不会上传到服务器
