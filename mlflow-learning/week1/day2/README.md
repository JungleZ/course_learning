# Day 2: 实验跟踪基础 - 深入理解MLFlow Tracking

## 🎯 今天的目标

- 理解MLFlow Tracking的核心概念
- 学会记录不同类型的实验数据
- 掌握MLFlow API的常用方法
- 运行一个包含多种记录的Demo

## 📚 核心概念（小白版）

MLFlow Tracking就像写日记，可以记录：

| 记录类型 | 说明 | 例子 |
|---------|------|------|
| **Parameters（参数）** | 模型的设置 | 学习率=0.01, 树深度=5 |
| **Metrics（指标）** | 模型的效果 | 准确率=95%, 损失=0.3 |
| **Artifacts（文件）** | 保存的任何文件 | 模型文件、图片、数据 |
| **Tags（标签）** | 给实验加备注 | "基准模型", "版本=v2" |

**重要概念：Run（运行）**
- 一次Run = 一次实验记录
- 每个Run都有唯一的ID
- 一个实验（Experiment）可以包含多个Run

## 💻 Demo 1: 记录各种类型的数据

创建文件 `week1/day2/tracking_demo.py`：

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import matplotlib.pyplot as plt
import numpy as np

# 设置跟踪服务器
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("鸢尾花实验-第二天")

print("🚀 开始Demo 1: 记录各种类型的数据\n")

with mlflow.start_run(run_name="完整记录示例") as run:
    run_id = run.info.run_id
    print(f"📝 Run ID: {run_id[:8]}...")
    
    # 1. 记录参数（Parameters）
    params = {
        "n_estimators": 100,      # 树的数量
        "max_depth": 10,           # 最大深度
        "random_state": 42         # 随机种子
    }
    mlflow.log_params(params)
    print(f"✅ 已记录参数: {params}")
    
    # 2. 加载数据并训练
    X, y = load_wine(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    
    # 3. 记录指标（Metrics）
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1_score", f1)
    print(f"✅ 已记录指标: accuracy={accuracy:.4f}, f1={f1:.4f}")
    
    # 4. 记录标签（Tags）
    mlflow.set_tags({
        "model_type": "RandomForest",
        "dataset": "wine",
        "purpose": "学习MLFlow Tracking",
        "author": "小白学员"
    })
    print("✅ 已记录标签")
    
    # 5. 记录模型（Artifacts - 模型）
    mlflow.sklearn.log_model(model, "random_forest_model")
    print("✅ 已保存模型")
    
    # 6. 记录文件（Artifacts - 图片）
    # 创建一个特征重要性的图片
    feature_names = [f"特征{i}" for i in range(X.shape[1])]
    importances = model.feature_importances_
    
    plt.figure(figsize=(10, 6))
    plt.barh(feature_names, importances)
    plt.xlabel("重要性")
    plt.title("随机森林特征重要性")
    plt.tight_layout()
    plt.savefig("feature_importance.png")
    plt.close()
    
    # 把图片记录到MLFlow
    mlflow.log_artifact("feature_importance.png")
    print("✅ 已保存特征重要性图片")
    
    # 7. 记录文本文件
    with open("experiment_notes.txt", "w", encoding="utf-8") as f:
        f.write("这次实验效果不错！\n")
        f.write(f"准确率达到了 {accuracy:.2%}\n")
        f.write("下次可以尝试调整 max_depth 参数\n")
    
    mlflow.log_artifact("experiment_notes.txt")
    print("✅ 已保存实验笔记")
    
    print(f"\n🎉 实验完成！查看: http://localhost:5000")

# 清理临时文件
import os
if os.path.exists("feature_importance.png"):
    os.remove("feature_importance.png")
if os.path.exists("experiment_notes.txt"):
    os.remove("experiment_notes.txt")
```

## ▶️ 运行Demo 1

```bash
# 确保MLFlow UI在另一个窗口运行着
# 新开一个命令行，激活虚拟环境，然后：
cd D:\code_workspaces\mlflow-learning
python week1/day2/tracking_demo.py
```

**预期输出：**
```
🚀 开始Demo 1: 记录各种类型的数据

📝 Run ID: abc123...
✅ 已记录参数: {'n_estimators': 100, 'max_depth': 10, 'random_state': 42}
✅ 已记录指标: accuracy=0.9722, f1=0.9722
✅ 已记录标签
✅ 已保存模型
✅ 已保存特征重要性图片
✅ 已保存实验笔记

🎉 实验完成！查看: http://localhost:5000
```

## 👀 在UI中查看

1. 刷新 http://localhost:5000
2. 点击 "鸢尾花实验-第二天"
3. 点击 "完整记录示例" 这个Run
4. 你会看到四个标签页：
   - **Parameters**: 看到3个参数
   - **Metrics**: 看到accuracy和f1_score
   - **Artifacts**: 看到模型、图片、文本文件
   - **Info**: 看到Tags标签

**试试点击 Artifacts 标签，下载那个图片看看！**

## 💻 Demo 2: 记录训练过程（分阶段记录指标）

很多时候我们需要记录训练过程中的指标变化，比如每训练一轮记录一次损失值。

创建文件 `week1/day2/logging_during_training.py`：

```python
import mlflow
import numpy as np

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("鸢尾花实验-第二天")

print("🚀 开始Demo 2: 模拟训练过程记录\n")

with mlflow.start_run(run_name="训练过程记录"):
    # 模拟训练过程：假设我们在训练10轮
    print("开始训练...")
    for epoch in range(1, 11):
        # 模拟：损失值逐渐下降
        loss = 1.0 / epoch + np.random.random() * 0.1
        accuracy = 0.5 + 0.05 * epoch - np.random.random() * 0.02
        
        # 记录这一轮的指标，step参数表示第几轮
        mlflow.log_metric("loss", loss, step=epoch)
        mlflow.log_metric("accuracy", accuracy, step=epoch)
        
        print(f"  Epoch {epoch:2d}: loss={loss:.4f}, accuracy={accuracy:.4f}")
    
    print("\n✅ 训练完成！现在去UI看看图表！")
    print("💡 提示：在Metrics标签页可以看到折线图")
```

运行：
```bash
python week1/day2/logging_during_training.py
```

**查看结果：** 在MLFlow UI中，点击这个Run，然后看Metrics标签，你会看到漂亮的折线图！

## 💻 Demo 3: 一次运行多个实验并比较

创建文件 `week1/day2/compare_experiments.py`：

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("鸢尾花实验-第二天")

print("🚀 开始Demo 3: 运行多个实验\n")

# 定义不同的参数组合
param_grid = [
    {"n_estimators": 50, "max_depth": 5, "run_name": "浅树-少树"},
    {"n_estimators": 50, "max_depth": 20, "run_name": "深树-少树"},
    {"n_estimators": 200, "max_depth": 5, "run_name": "浅树-多树"},
    {"n_estimators": 200, "max_depth": 20, "run_name": "深树-多树"},
]

# 加载数据（只需一次）
X, y = load_wine(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 运行4次实验
for i, params in enumerate(param_grid, 1):
    run_name = params.pop("run_name")
    
    with mlflow.start_run(run_name=run_name):
        print(f"\n实验 {i}: {run_name}")
        print(f"  参数: n_estimators={params['n_estimators']}, max_depth={params['max_depth']}")
        
        # 记录参数
        mlflow.log_params(params)
        
        # 训练模型
        model = RandomForestClassifier(**params, random_state=42)
        model.fit(X_train, y_train)
        
        # 评估
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # 记录指标
        mlflow.log_metric("accuracy", accuracy)
        
        # 保存最好的模型
        mlflow.sklearn.log_model(model, "model")
        
        print(f"  准确率: {accuracy:.2%}")
        
        # 给最好的模型打个标签
        if accuracy > 0.95:
            mlflow.set_tag("performance", "优秀")
        else:
            mlflow.set_tag("performance", "一般")

print("\n🎉 4个实验完成！现在去UI比较它们！")
print("💡 提示：在实验列表勾选多个Run，点击Compare按钮")
```

运行：
```bash
python week1/day2/compare_experiments.py
```

**比较实验：** 在MLFlow UI中，勾选多个Run（打勾），然后点击上方的"Compare"按钮，可以并排比较参数和指标！

## 📝 今天学到的API总结

```python
# 1. 设置跟踪服务器和实验
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("实验名称")

# 2. 开始一个实验运行
with mlflow.start_run(run_name="给这次运行起个名"):
    # 3. 记录参数（一次一个或一次多个）
    mlflow.log_param("参数名", 值)
    mlflow.log_params({"参数1": 值1, "参数2": 值2})
    
    # 4. 记录指标（可以带step表示训练轮次）
    mlflow.log_metric("指标名", 值)
    mlflow.log_metric("指标名", 值, step=轮次)
    
    # 5. 设置标签
    mlflow.set_tag("标签名", "标签值")
    mlflow.set_tags({"标签1": "值1", "标签2": "值2"})
    
    # 6. 保存模型（sklearn例子）
    mlflow.sklearn.log_model(模型对象, "保存名称")
    
    # 7. 保存文件
    mlflow.log_artifact("文件路径")
```

## 🎓 今天总结

- ✅ 理解了Parameters、Metrics、Artifacts、Tags
- ✅ 学会了记录训练过程的指标变化（带step）
- ✅ 运行了多个实验并比较
- ✅ 掌握了MLFlow Tracking的核心API

## 📝 小练习

1. 修改 `compare_experiments.py`，添加一个新的参数 `min_samples_split`，试试不同的值
2. 在MLFlow UI中，尝试给某个Run添加笔记（点击Run名字，在Notes里添加）

## 🚀 下一步

明天我们将用一个完整的鸢尾花分类项目，把学到的知识串起来！

👉 **明天见： [Day 3 - 鸢尾花分类完整实战](D:\code_workspaces\mlflow-learning\week1\day3\)**
