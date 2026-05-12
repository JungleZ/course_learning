# Day 5：Streamlit 可视化部署

## 🎯 今日目标
1. 学习用 Streamlit 快速构建 ML 应用界面
2. 部署到 Streamlit Community Cloud（免费！）
3. 体验零前端代码构建交互式应用

---

## 🤔 为什么用 Streamlit？

| 方式 | 需要前端知识 | 开发时间 | 交互性 | 部署难度 |
|------|------------|---------|--------|---------|
| Flask + HTML | ✅ 需要 | 数小时 | 中等 | 中等 |
| FastAPI + 前端 | ✅ 需要 | 数天 | 高 | 较高 |
| **Streamlit** | ❌ 不需要 | **几分钟** | **高** | **极简** |

**Streamlit = 用纯 Python 写 Web 界面，不用写一行 HTML/CSS/JS！**

---

## 📁 项目结构

```
day05-streamlit/
├── guide.md     # 本文件
└── app.py       # Streamlit 应用
```

---

## 🚀 运行步骤

### 第1步：安装 Streamlit
```bash
pip install streamlit
```

### 第2步：运行应用
```bash
cd day05-streamlit
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

### 第3步：体验功能
- 调整侧边栏的滑块，观察预测结果实时变化
- 查看模型可视化和概率分布图
- 上传 CSV 文件批量预测

---

## ☁️ 部署到 Streamlit Community Cloud（免费！）

### 步骤：
1. 把代码推送到 GitHub 仓库
2. 访问 https://streamlit.io/cloud
3. 点击 "New app"
4. 选择你的 GitHub 仓库
5. 点击 "Deploy"
6. 🎉 几分钟后，你的应用就上线了！

### 需要额外文件：
- `requirements.txt` - Python 依赖
- `packages.txt` - 系统依赖（如需要）

---

## 🔑 Streamlit 常用组件

| 组件 | 作用 | 示例 |
|------|------|------|
| `st.slider` | 滑块输入 | `st.slider("长度", 0.0, 10.0)` |
| `st.selectbox` | 下拉选择 | `st.selectbox("品种", ["A","B"])` |
| `st.button` | 按钮 | `st.button("预测")` |
| `st.dataframe` | 显示表格 | `st.dataframe(df)` |
| `st.pyplot` | 显示图表 | `st.pyplot(fig)` |
| `st.file_uploader` | 文件上传 | `st.file_uploader("上传CSV")` |
| `st.columns` | 多列布局 | `col1, col2 = st.columns(2)` |
| `st.sidebar` | 侧边栏 | `st.sidebar.slider(...)` |
| `st.cache_resource` | 缓存模型 | 避免每次交互都重新加载 |

---

## 📊 部署架构

```
┌──────────────────────────────┐
│       Streamlit 应用          │
│  ┌─────────┐  ┌───────────┐ │
│  │ 侧边栏   │  │  主内容区   │ │
│  │ 滑块输入  │  │  预测结果   │ │
│  │ 参数设置  │  │  可视化图表 │ │
│  └─────────┘  └───────────┘ │
│         ↓                    │
│    模型推理（内存中）          │
└──────────────────────────────┘
         ↕
    Streamlit Cloud / 本地
```

---

## ✅ 今日检查清单
- [ ] 成功安装 Streamlit
- [ ] 运行 app.py 看到交互界面
- [ ] 调整滑块，预测结果实时变化
- [ ] 了解 Streamlit Cloud 部署流程
- [ ] 理解 Streamlit 的优势和适用场景

## 🎉 完成 Day 5！明天学习 Gradio 快速构建 Demo。
