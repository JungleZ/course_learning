# Day 1: MLFlow是什么？为什么要学？

## 🎯 今天的目标

- 理解MLFlow是干什么的
- 成功安装MLFlow
- 运行第一个MLFlow实验
- 看到MLFlow的界面

## 🤔 MLFlow是什么？（小白版解释）

想象你在上学做实验：

**没有MLFlow的时候：**
- 你做了10次实验，每次改一点点参数
- 你记在本子上：第1次准确率80%，第2次82%...
- 过了两周，你忘了哪次效果最好，参数怎么设的了
- 文件名变成：model_final.ipynb, model_final_v2.ipynb, model_really_final.ipynb...

**有了MLFlow之后：**
- 每次实验自动记录：用了什么参数、得到什么结果、保存了什么模型
- 有个网页界面，点点鼠标就能对比哪次实验最好
- 想复现某次实验？点一下就能看到所有细节

**一句话总结：** MLFlow就是机器学习版的"实验记录本"，而且比手写记录强大100倍！

## 📦 第一步：安装MLFlow

打开你的命令行（cmd或PowerShell），跟着做：

```bash
# 1. 确保你在项目目录
cd D:\code_workspaces\mlflow-learning

# 2. 创建虚拟环境（就像给这个项目准备一个独立的工具箱）
python -m venv .venv

# 3. 激活虚拟环境
# Windows用户：
.venv\Scripts\activate
# Mac/Linux用户：
# source .venv/bin/activate

# 4. 安装MLFlow和常用的机器学习库
pip install mlflow scikit-learn pandas numpy

# 5. 验证安装成功
python -c "import mlflow; print('MLFlow版本:', mlflow.__version__)"
```

如果看到输出MLFlow版本号，恭喜你安装成功了！✅

## 🚀 第二步：启动MLFlow界面

```bash
# 在命令行输入（确保虚拟环境已激活）
mlflow ui

# 看到类似这样的输出就成功了：
# [INFO] Listening on http://127.0.0.1:5000
```

现在打开浏览器，访问：**http://localhost:5000**

你会看到一个网页界面，这就是MLFlow的"控制面板"。现在还是空的，因为我们还没记录任何实验。

**别关这个命令行窗口！** 保持它运行，我们接下来要用。

## 💻 第三步：第一个MLFlow实验

新建一个文件 `week1/day1/first_experiment.py`，把下面的代码复制进去：

```python
import mlflow
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 告诉MLFlow把实验记录保存在哪里（本地文件夹）
mlflow.set_tracking_uri("http://127.0.0.1:5000")

# 创建一个实验（就像在记录本上开个新章节）
mlflow.set_experiment("我的第一个实验")

# 开始记录一次实验
with mlflow.start_run(run_name="第一次尝试"):
    print("🚀 开始训练模型...")
    
    # 1. 加载数据（鸢尾花数据集，机器学习的"Hello World"）
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 2. 设置模型参数（这就是我们要记录的）
    params = {
        "C": 1.0,           # 正则化参数
        "solver": "lbfgs",   # 求解器
        "max_iter": 100      # 最大迭代次数
    }
    
    # 记录参数到MLFlow
    mlflow.log_params(params)
    print(f"📝 参数已记录: {params}")
    
    # 3. 训练模型
    model = LogisticRegression(**params)
    model.fit(X_train, y_train)
    print("✅ 模型训练完成!")
    
    # 4. 评估模型
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # 记录指标到MLFlow
    mlflow.log_metric("accuracy", accuracy)
    print(f"📊 准确率: {accuracy:.2%}")
    
    # 5. 保存模型到MLFlow
    mlflow.sklearn.log_model(model, "model")
    print("💾 模型已保存到MLFlow!")
    
    print("\n🎉 实验完成！去 http://localhost:5000 看看吧！")
```

## ▶️ 运行你的第一个实验

```bash
# 确保你在项目根目录，且虚拟环境已激活
cd D:\code_workspaces\mlflow-learning

# 运行脚本
python week1/day1/first_experiment.py
```

看到类似这样的输出就成功了：

```
🚀 开始训练模型...
📝 参数已记录: {'C': 1.0, 'solver': 'lbfgs', 'max_iter': 100}
✅ 模型训练完成!
📊 准确率: 96.67%
💾 模型已保存到MLFlow!
🎉 实验完成！去 http://localhost:5000 看看吧！
```

## 👀 第四步：查看实验结果

1. 回到浏览器，刷新 http://localhost:5000
2. 点击 "我的第一个实验"
3. 你会看到 "第一次尝试" 这个实验记录
4. 点击进去，能看到：
   - **Parameters（参数）**: C=1.0, solver=lbfgs...
   - **Metrics（指标）**: accuracy=0.9667
   - **Artifacts（模型文件）**: 保存的模型

**试试看：** 在页面上你能找到这些信息吗？找到就说明你成功了！🎉

## 🎓 今天学到了什么？

- ✅ MLFlow是一个实验跟踪工具
- ✅ 安装了MLFlow
- ✅ 启动了MLFlow UI界面
- ✅ 运行了第一个实验，记录了参数、指标和模型
- ✅ 在网页上看到了实验结果

## 📝 小练习（可选）

尝试修改 `first_experiment.py` 中的参数，比如把 `C` 改成 `0.5`，再运行一次。然后去MLFlow界面看看，是不是有两条实验记录了？

## 🤔 常见问题

**Q: 我运行脚本时报错 "connection refused"？**
A: 确保你运行了 `mlflow ui` 并且没关那个窗口。MLFlow界面必须在运行状态。

**Q: 我找不到mlflow命令？**
A: 确保虚拟环境已激活（命令行前面有 `(.venv)` 字样）。

**Q: 为什么要创建虚拟环境？**
A: 就像给每个项目准备独立的工具箱，避免不同项目的库版本冲突。

## 🚀 下一步

明天我们将深入学习MLFlow Tracking API，了解如何更灵活地记录实验数据。

👉 **明天见： [Day 2 - 实验跟踪基础](D:\code_workspaces\mlflow-learning\week1\day2\)**
