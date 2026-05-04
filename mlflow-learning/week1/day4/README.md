# Day 4: 比较实验结果 - 找出最佳模型

## 🎯 今天的目标

- 学会在MLFlow中搜索和筛选实验
- 使用代码自动找到最佳模型
- 理解如何通过可视化比较实验
- 掌握MLFlow的查询API

## 🤔 为什么需要比较实验？

在实际项目中，你可能会跑几十上百次实验：
- 不同的模型（随机森林、SVM、神经网络...）
- 不同的参数组合（学习率、树的深度...）
- 不同的数据预处理方式

**问题来了：** 怎么快速找到最好的那个实验？

今天教你3种方法：
1. **手动比较**：在MLFlow UI中点选比较
2. **代码搜索**：用MLFlow API搜索最佳实验
3. **可视化**：画出参数和指标的关系图

## 💻 Demo 1: 运行大量实验（模拟超参数搜索）

创建文件 `week1/day4/hyperparameter_search.py`：

```python
"""
模拟超参数搜索 - 运行很多实验并记录到MLFlow
"""

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("超参数搜索-Day4")

print("🌲 开始随机森林超参数搜索...\n")

# 加载数据
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 定义要搜索的参数范围
n_estimators_list = [10, 50, 100, 200]
max_depth_list = [None, 5, 10, 20]
random_state = 42

# 运行16次实验（4x4组合）
run_count = 0

for n_est in n_estimators_list:
    for max_dp in max_depth_list:
        run_count += 1
        
        with mlflow.start_run(run_name=f"搜索-第{run_count}次") as run:
            # 记录参数
            params = {
                "n_estimators": n_est,
                "max_depth": max_dp if max_dp else -1,  # -1表示None
                "random_state": random_state
            }
            mlflow.log_params(params)
            
            # 训练模型
            if max_dp:
                model = RandomForestClassifier(
                    n_estimators=n_est, 
                    max_depth=max_dp, 
                    random_state=random_state
                )
            else:
                model = RandomForestClassifier(
                    n_estimators=n_est, 
                    max_depth=None, 
                    random_state=random_state
                )
            
            model.fit(X_train, y_train)
            
            # 评估
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # 记录指标
            mlflow.log_metric("accuracy", accuracy)
            
            # 保存模型（只保存准确率>0.9的）
            if accuracy > 0.9:
                mlflow.sklearn.log_model(model, "model")
                mlflow.set_tag("good_model", "yes")
            else:
                mlflow.set_tag("good_model", "no")
            
            # 打印进度
            depth_str = str(max_dp) if max_dp else "None"
            print(f"  实验{run_count:2d}: n_est={n_est:3d}, depth={depth_str:5s} -> accuracy={accuracy:.2%}")

print(f"\n✅ 完成！共运行了 {run_count} 次实验")
print(f"📊 查看结果: http://localhost:5000")
print(f"   实验名称: '超参数搜索-Day4'")
```

## ▶️ 运行Demo 1

```bash
python week1/day4/hyperparameter_search.py
```

**预期输出：**
```
🌲 开始随机森林超参数搜索...

  实验 1: n_est= 10, depth=None  -> accuracy=96.67%
  实验 2: n_est= 10, depth=    5  -> accuracy=96.67%
  ...（共16次）
  
✅ 完成！共运行了 16 次实验
📊 查看结果: http://localhost:5000
```

## 👀 方法1：在UI中手动比较

1. 打开 http://localhost:5000
2. 点击 "超参数搜索-Day4"
3. 你会看到16条实验记录
4. **排序功能**：点击 "accuracy" 列头，按准确率排序
5. **筛选功能**：点击 "Filter"，输入 `metrics.accuracy > 0.95`
6. **比较功能**：勾选前3个实验，点击 "Compare"

**试试看：** 你能找到准确率最高的那次实验吗？

## 💻 Demo 2: 用代码搜索最佳实验

创建文件 `week1/day4/find_best_model.py`：

```python
"""
使用MLFlow API搜索最佳实验并加载模型
"""

import mlflow
import mlflow.sklearn

mlflow.set_tracking_uri("http://127.0.0.1:5000")

print("🔍 搜索最佳实验...\n")

# 方法1: 使用mlflow.search_runs()搜索
experiment = mlflow.get_experiment_by_name("超参数搜索-Day4")

# 搜索所有实验，按准确率降序排序
runs = mlflow.search_runs(
    experiment_names=["超参数搜索-Day4"],
    order_by=["metrics.accuracy DESC"],  # 按准确率从高到低
    max_results=5  # 只要前5个
)

print("🏆 Top 5 实验（按准确率排序）:\n")
print(runs[['run_id', 'metrics.accuracy', 'params.n_estimators', 'params.max_depth']].to_string())

# 获取最佳实验
best_run = runs.iloc[0]
best_run_id = best_run['run_id']
best_accuracy = best_run['metrics.accuracy']

print(f"\n🥇 最佳实验:")
print(f"   Run ID: {best_run_id[:8]}...")
print(f"   准确率: {best_accuracy:.2%}")
print(f"   参数: n_estimators={int(best_run['params.n_estimators'])}, max_depth={best_run['params.max_depth']}")

# 加载最佳模型
print(f"\n📥 加载最佳模型...")
best_model_uri = f"runs:/{best_run_id}/model"
best_model = mlflow.sklearn.load_model(best_model_uri)

print(f"✅ 模型加载成功！")

# 测试模型
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
test_sample = X[:3]  # 取前3个样本
predictions = best_model.predict(test_sample)

print(f"\n🧪 测试预测:")
for i in range(3):
    print(f"  样本{i+1}: 真实={y[i]}, 预测={predictions[i]}")

# 方法2: 用filter字符串搜索
print(f"\n🔎 搜索准确率>95%的实验:")
good_runs = mlflow.search_runs(
    experiment_names=["超参数搜索-Day4"],
    filter_string="metrics.accuracy > 0.95"
)
print(f"  找到 {len(good_runs)} 个实验准确率超过95%")

# 方法3: 搜索带特定标签的实验
print(f"\n🏷️ 搜索标签为 good_model=yes 的实验:")
tagged_runs = mlflow.search_runs(
    experiment_names=["超参数搜索-Day4"],
    filter_string="tags.good_model = 'yes'"
)
print(f"  找到 {len(tagged_runs)} 个标记为'好模型'的实验")
```

## ▶️ 运行Demo 2

```bash
python week1/day4/find_best_model.py
```

**预期输出：**
```
🔍 搜索最佳实验...

🏆 Top 5 实验（按准确率排序）:

                              run_id  metrics.accuracy  params.n_estimators  params.max_depth
0  abc123def456...                1.0                  200                -1
1  def456ghi789...                1.0                  100                -1
...

🥇 最佳实验:
   Run ID: abc123...
   准确率: 100.00%
   参数: n_estimators=200, max_depth=-1

📥 加载最佳模型...
✅ 模型加载成功！

🧪 测试预测:
  样本1: 真实=0, 预测=0
  样本2: 真实=0, 预测=0
  样本3: 真实=0, 预测=0
```

## 💻 Demo 3: 可视化实验结果

创建文件 `week1/day4/visualize_results.py`：

```python
"""
可视化实验结果 - 用图表展示参数和指标的关系
"""

import mlflow
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

mlflow.set_tracking_uri("http://127.0.0.1:5000")

print("📊 可视化实验结果...\n")

# 获取所有实验数据
runs = mlflow.search_runs(
    experiment_names=["超参数搜索-Day4"],
    order_by=["metrics.accuracy DESC"]
)

print(f"共获取 {len(runs)} 条实验记录\n")

# 转换数据：处理max_depth为None的情况（-1表示None）
runs['max_depth_clean'] = runs['params.max_depth'].apply(
    lambda x: 'None' if x == -1 else str(int(x))
)

# 设置绘图风格
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10

# 图1: 不同n_estimators的准确率分布
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
sns.boxplot(data=runs, x='params.n_estimators', y='metrics.accuracy')
plt.title('树数量 vs 准确率')
plt.xlabel('n_estimators')
plt.ylabel('Accuracy')

# 图2: 不同max_depth的准确率分布
plt.subplot(1, 3, 2)
sns.boxplot(data=runs, x='max_depth_clean', y='metrics.accuracy')
plt.title('树深度 vs 准确率')
plt.xlabel('max_depth')
plt.ylabel('Accuracy')

# 图3: 散点图 - 两个参数的组合效果
plt.subplot(1, 3, 3)
scatter = plt.scatter(
    runs['params.n_estimators'], 
    runs['metrics.accuracy'],
    c=runs['params.max_depth'],  # 颜色表示深度
    cmap='viridis',
    s=100,
    alpha=0.7
)
plt.colorbar(scatter, label='max_depth')
plt.title('参数组合效果')
plt.xlabel('n_estimators')
plt.ylabel('Accuracy')

plt.tight_layout()
plt.savefig("experiment_analysis.png", dpi=100)
plt.show()

print("✅ 图表已保存为 experiment_analysis.png")
print("💡 提示：查看图片，找出哪个参数组合效果最好")
```

## ▶️ 运行Demo 3

```bash
pip install seaborn  # 如果还没安装
python week1/day4/visualize_results.py
```

这会弹出3个图表，帮你直观理解参数对结果的影响。

## 📝 MLFlow搜索API总结

```python
import mlflow

# 1. 搜索实验
runs = mlflow.search_runs(
    experiment_names=["实验名称"],
    filter_string="metrics.accuracy > 0.9",  # 筛选条件
    order_by=["metrics.accuracy DESC"],        # 排序
    max_results=10                              # 返回数量
)

# 2. 常用筛选条件
# 按指标筛选：
"metrics.accuracy > 0.9"
"metrics.loss < 0.5"

# 按参数筛选：
"params.learning_rate = '0.01'"
"params.n_estimators > 100"

# 按标签筛选：
"tags.model_type = 'RandomForest'"

# 组合筛选：
"metrics.accuracy > 0.9 and params.n_estimators >= 100"

# 3. 获取实验信息
experiment = mlflow.get_experiment_by_name("实验名称")
print(f"Experiment ID: {experiment.experiment_id}")
```

## 🎓 今天总结

- ✅ 学会了运行大量实验（超参数搜索）
- ✅ 掌握了在UI中筛选、排序、比较实验
- ✅ 学会了用代码搜索最佳实验
- ✅ 用可视化理解参数对结果的影响

## 📝 小练习

1. **修改搜索范围**：在 `hyperparameter_search.py` 中添加 `min_samples_split` 参数，看看效果
2. **添加新指标**：除了accuracy，再记录 `training_time`（训练时间）
3. **挑战题**：写代码自动找到最好的前3个实验，并把它们的模型都加载出来比较

## 🚀 下一步

明天我们将学习MLFlow Projects，让你的代码可以在任何机器上复现！

👉 **明天见： [Day 5 - MLFlow Projects](D:\code_workspaces\mlflow-learning\week1\day5\)**
