# Day 6：Gradio 快速构建 Demo

## 🎯 今日目标
1. 学习用 Gradio 快速构建 ML Demo
2. 部署到 HuggingFace Spaces（免费！）
3. 对比 Gradio 与 Streamlit 的适用场景

---

## 🤔 Gradio vs Streamlit

| 特性 | Streamlit | Gradio |
|------|-----------|--------|
| 学习曲线 | 简单 | **更简单** |
| 代码量 | 少 | **更少** |
| 部署平台 | Streamlit Cloud | **HuggingFace Spaces** |
| 适合场景 | 数据应用、仪表盘 | **ML Demo、模型展示** |
| 前端定制 | 较灵活 | 有限 |
| 社区热度 | 高 | 高 |

**Gradio = 几行代码就能做一个 ML Demo，特别适合展示模型效果！**

---

## 📁 项目结构

```
day06-gradio/
├── guide.md     # 本文件
└── app.py       # Gradio 应用
```

---

## 🚀 运行步骤

### 第1步：安装 Gradio
```bash
pip install gradio
```

### 第2步：运行应用
```bash
cd day06-gradio
python app.py
```

浏览器自动打开 http://127.0.0.1:7860

### 第3步：体验功能
- 输入花的测量数据，点击"预测"
- 查看预测结果和概率分布
- 体验不同的 Gradio 组件

---

## ☁️ 部署到 HuggingFace Spaces

### 步骤：
1. 注册 HuggingFace 账号：https://huggingface.co/join
2. 创建新 Space：https://huggingface.co/new-space
3. 选择 SDK：**Gradio**
4. 上传以下文件：
   - `app.py` - 主应用
   - `requirements.txt` - 依赖
5. 🎉 自动构建部署，几分钟就上线！

### requirements.txt 内容：
```
scikit-learn
numpy
```

---

## 🔑 Gradio 常用组件

| 组件 | 作用 | 示例 |
|------|------|------|
| `gr.Slider` | 滑块 | `gr.Slider(0, 10, label="长度")` |
| `gr.Textbox` | 文本输入 | `gr.Textbox(label="输入")` |
| `gr.Image` | 图片输入 | `gr.Image(type="pil")` |
| `gr.Audio` | 音频输入 | `gr.Audio(source="microphone")` |
| `gr.Dataframe` | 表格输出 | `gr.Dataframe()` |
| `gr.Label` | 分类标签 | `gr.Label(num_top_classes=3)` |
| `gr.Plot` | 图表输出 | `gr.Plot()` |
| `gr.Examples` | 示例数据 | `gr.Examples([...], inputs=[...])` |

---

## 📊 部署架构

```
┌────────────────────────────┐
│      Gradio 界面            │
│  ┌───────┐  ┌───────────┐ │
│  │ 输入区 │→ │  预测函数   │ │
│  │ 滑块   │  │  predict() │ │
│  │ 按钮   │  │            │ │
│  └───────┘  └─────┬─────┘ │
│                    ↓       │
│             ┌───────────┐ │
│             │  输出区     │ │
│             │  标签+概率  │ │
│             └───────────┘ │
└────────────────────────────┘
         ↕
  HuggingFace Spaces / 本地
```

---

## ✅ 今日检查清单
- [ ] 成功安装 Gradio
- [ ] 运行 app.py 看到交互界面
- [ ] 输入数据并获取预测结果
- [ ] 了解 HuggingFace Spaces 部署流程
- [ ] 理解 Gradio 和 Streamlit 的区别

## 🎉 完成 Day 6 + 第一周总结！明天休息，后天开始第二周！
