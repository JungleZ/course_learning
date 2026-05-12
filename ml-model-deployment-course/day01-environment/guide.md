# Day 1：环境搭建 + 训练第一个模型

## 🎯 今日目标
1. 安装 Python 和必要工具
2. 搭建机器学习开发环境
3. 训练你的第一个机器学习模型

---

## 📥 第一步：安装 Python

### Windows 用户
1. 打开浏览器，访问 https://www.python.org/downloads/
2. 下载最新版 Python（3.9 或以上）
3. **⚠️ 重要：安装时勾选 "Add Python to PATH"**（这一步很多人忘记！）
4. 点击 "Install Now"

### 验证安装
打开命令行（Win+R 输入 cmd），输入：
```bash
python --version
# 应该显示 Python 3.9.x 或更高版本

pip --version
# 应该显示 pip 21.x 或更高版本
```

---

## 📦 第二步：安装必要的库

打开命令行，**一条一条**执行以下命令：

```bash
# 基础科学计算库
pip install numpy

# 数据处理库
pip install pandas

# 机器学习核心库（最重要！）
pip install scikit-learn

# 深度学习框架（选一个安装即可）
pip install torch          # PyTorch（推荐，课程主要使用）
# 或者
pip install tensorflow     # TensorFlow

# 可视化库
pip install matplotlib

# 后续部署用的库（提前装好）
pip install flask
pip install fastapi uvicorn
pip install streamlit
pip install gradio
```

### 💡 如果下载太慢，使用国内镜像源：
```bash
pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 🏋️ 第三步：训练第一个模型

我们用最经典的 **鸢尾花分类** 任务来入门。

### 什么是鸢尾花分类？
- 有 3 种鸢尾花：山鸢尾、变色鸢尾、维吉尼亚鸢尾
- 通过花萼和花瓣的长度、宽度来预测品种
- 这是一个**分类问题**（给定特征，预测类别）

### 运行代码
```bash
cd day01-environment
python train_first_model.py
```

---

## 🐛 常见问题

### Q: 提示 "python 不是内部命令"
A: 安装时没勾选 "Add Python to PATH"。解决方案：
1. 重新运行安装程序，勾选 PATH 选项
2. 或者手动添加 Python 安装路径到系统环境变量

### Q: pip install 很慢或超时
A: 使用清华镜像源：
```bash
pip install 包名 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 提示权限不足
A: Windows 上用管理员身份运行 cmd，或者加 `--user` 参数：
```bash
pip install 包名 --user
```

---

## ✅ 今日检查清单
- [ ] Python 安装成功，`python --version` 正常输出
- [ ] pip 安装成功，`pip --version` 正常输出
- [ ] scikit-learn 安装成功
- [ ] PyTorch 或 TensorFlow 安装成功
- [ ] 运行 `train_first_model.py` 成功，看到模型准确率输出

## 🎉 完成 Day 1！明天我们学习如何保存和加载模型。
