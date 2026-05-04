# Day 3: 鸢尾花分类完整实战

## 🎯 今天的目标

- 完成一个完整的机器学习项目
- 用MLFlow记录整个流程
- 理解从数据到模型的全过程
- 学会查看和加载保存的模型

## 📖 项目说明

今天我们要做一个**鸢尾花分类**项目。这是机器学习界的"Hello World"，非常简单但包含完整流程。

**任务：** 根据鸢尾花的4个特征（花萼长、花萼宽、花瓣长、花瓣宽），预测它属于哪个品种（Setosa、Versicolor、Virginica）。

## 💻 完整项目代码

创建文件 `week1/day3/iris_classifier.py`：

```python
"""
鸢尾花分类完整项目 - 使用MLFlow跟踪
这是适合小白的完整示例，每个步骤都有详细注释
"""

import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# ========== 配置部分 ==========
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("鸢尾花完整项目-Day3")

print("🌸 鸢尾花分类项目开始！\n")
print("=" * 50)

# ========== 步骤1: 加载和探索数据 ==========
print("\n📊 步骤1: 加载数据...")

# 加载鸢尾花数据集
iris = load_iris()
X = iris.data  # 特征：花萼长、花萼宽、花瓣长、花瓣宽
y = iris.target  # 标签：0, 1, 2 (三个品种)
feature_names = iris.feature_names
target_names = iris.target_names

print(f"  数据集大小: {X.shape}")
print(f"  特征: {feature_names}")
print(f"  品种: {target_names}")

# 转换为DataFrame方便查看
df = pd.DataFrame(X, columns=feature_names)
df['品种'] = [target_names[i] for i in y]
print("\n  数据预览:")
print(df.head())

# ========== 步骤2: 划分训练集和测试集 ==========
print("\n✂️ 步骤2: 划分数据集...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.3,      # 30%作为测试集
    random_state=42,     # 随机种子，保证结果可复现
    stratify=y           # 按品种比例划分
)

print(f"  训练集: {X_train.shape[0]} 个样本")
print(f"  测试集: {X_test.shape[0]} 个样本")

# ========== 步骤3: 数据预处理 ==========
print("\n🔧 步骤3: 数据标准化...")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # 拟合+转换训练集
X_test_scaled = scaler.transform(X_test)        # 只转换测试集

print("  标准化完成！(让每个特征的均值为0，标准差为1)")

# ========== 步骤4: 训练模型（使用MLFlow记录） ==========
print("\n🚀 步骤4: 训练模型...")

# 我们使用MLFlow记录两次实验：逻辑回归 vs 随机森林
models = {
    "逻辑回归": LogisticRegression(max_iter=200),
    "随机森林": RandomForestClassifier(n_estimators=100, random_state=42)
}

best_model = None
best_accuracy = 0

for model_name, model in models.items():
    print(f"\n  训练模型: {model_name}")
    
    # 开始一次MLFlow运行
    with mlflow.start_run(run_name=f"{model_name}-鸢尾花") as run:
        run_id = run.info.run_id
        
        # 记录模型类型标签
        mlflow.set_tag("model_type", model_name)
        mlflow.set_tag("dataset", "iris")
        mlflow.set_tag("task", "classification")
        
        # 记录参数
        if model_name == "逻辑回归":
            params = {"C": 1.0, "max_iter": 200, "solver": "lbfgs"}
        else:  # 随机森林
            params = {"n_estimators": 100, "random_state": 42}
        
        mlflow.log_params(params)
        
        # 训练模型
        model.fit(X_train_scaled, y_train)
        
        # 预测
        y_pred = model.predict(X_test_scaled)
        
        # 计算准确率
        accuracy = accuracy_score(y_test, y_pred)
        
        # 记录指标
        mlflow.log_metric("accuracy", accuracy)
        
        print(f"    准确率: {accuracy:.2%}")
        
        # 保存标准化器（因为预测时也需要用）
        mlflow.log_sklearn_model(
            sk_model=model,  # 模型
            artifact_path="model",  # 保存路径
            # 保存预处理器的技巧：把scaler作为一个artifact
        )
        
        # 记录标准化器
        joblib.dump(scaler, "scaler.pkl")
        mlflow.log_artifact("scaler.pkl")
        
        # 记录混淆矩阵图片
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=target_names, yticklabels=target_names)
        plt.title(f'{model_name} - 混淆矩阵')
        plt.ylabel('真实标签')
        plt.xlabel('预测标签')
        plt.tight_layout()
        plt.savefig("confusion_matrix.png")
        mlflow.log_artifact("confusion_matrix.png")
        plt.close()
        
        # 记录分类报告
        report = classification_report(y_test, y_pred, target_names=target_names)
        with open("classification_report.txt", "w", encoding="utf-8") as f:
            f.write(f"{model_name} 分类报告\n")
            f.write("=" * 50 + "\n")
            f.write(report)
        mlflow.log_artifact("classification_report.txt")
        
        print(f"    ✅ 实验已记录到MLFlow! Run ID: {run_id[:8]}...")
        
        # 判断是否是当前最好的模型
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model_name
            best_run_id = run_id

print(f"\n🏆 最佳模型: {best_model} (准确率: {best_accuracy:.2%})")

# ========== 步骤5: 加载并使用最好的模型 ==========
print("\n📥 步骤5: 加载最佳模型进行预测...")

# 使用MLFlow加载模型
best_model_uri = f"runs:/{best_run_id}/model"
loaded_model = mlflow.sklearn.load_model(best_model_uri)

# 新数据预测示例
new_flower = [[5.1, 3.5, 1.4, 0.2]]  # 一朵新鸢尾花的特征
new_flower_scaled = scaler.transform(new_flower)  # 记得标准化！
prediction = loaded_model.predict(new_flower_scaled)
predicted_species = target_names[prediction[0]]

print(f"  新鸢尾花特征: {new_flower[0]}")
print(f"  预测品种: {predicted_species}")

# ========== 清理临时文件 ==========
import os
for f in ["scaler.pkl", "confusion_matrix.png", "classification_report.txt"]:
    if os.path.exists(f):
        os.remove(f)

print("\n" + "=" * 50)
print("🎉 项目完成！")
print(f"📊 查看实验结果: http://localhost:5000")
print(f"   实验名称: '鸢尾花完整项目-Day3'")
print("=" * 50)
```

## ▶️ 运行完整项目

```bash
cd D:\code_workspaces\mlflow-learning

# 确保MLFlow UI在另一个窗口运行
# 激活虚拟环境后运行：
python week1/day3/iris_classifier.py
```

**预期输出：**
```
🌸 鸢尾花分类项目开始！

==================================================
📊 步骤1: 加载数据...
  数据集大小: (150, 4)
  特征: ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
  品种: ['setosa' 'versicolor' 'virginica']

  数据预览:
   sepal length (cm)  ...  品种
0                5.1  ...  setosa
1                4.9  ...  setosa
...

✂️ 步骤2: 划分数据集...
  训练集: 105 个样本
  测试集: 45 个样本

🔧 步骤3: 数据标准化...
  标准化完成！

🚀 步骤4: 训练模型...

  训练模型: 逻辑回归
    准确率: 97.78%
    ✅ 实验已记录到MLFlow! Run ID: abc123...

  训练模型: 随机森林
    准确率: 100.00%
    ✅ 实验已记录到MLFlow! Run ID: def456...

🏆 最佳模型: 随机森林 (准确率: 100.00%)

📥 步骤5: 加载最佳模型进行预测...
  新鸢尾花特征: [5.1, 3.5, 1.4, 0.2]
  预测品种: setosa

==================================================
🎉 项目完成！
📊 查看实验结果: http://localhost:5000
==================================================
```

## 👀 在MLFlow UI中查看

1. 打开 http://localhost:5000
2. 点击 "鸢尾花完整项目-Day3"
3. 你会看到两个Run：
   - "逻辑回归-鸢尾花"
   - "随机森林-鸢尾花"
4. 点击每个Run查看：
   - **Parameters**: 模型参数
   - **Metrics**: 准确率
   - **Artifacts**: 模型文件、混淆矩阵图片、分类报告
   - **Info**: 标签信息

**试试看：**
- 勾选两个Run，点击"Compare"比较它们
- 下载混淆矩阵图片看看
- 查看分类报告文本内容

## 🎓 今天学到了什么？

- ✅ 完整的机器学习项目流程
- ✅ 数据加载、划分、预处理
- ✅ 训练多个模型并用MLFlow比较
- ✅ 保存和加载模型
- ✅ 记录图片和文本文件到MLFlow

## 📝 小练习

1. **添加新模型**：在 `models` 字典里添加 `SVC()` (支持向量机)，看看效果如何
2. **调整参数**：修改随机森林的 `n_estimators` 为 50 或 200，观察准确率变化
3. **添加新指标**：除了准确率，再记录 F1-score（需要 `from sklearn.metrics import f1_score`）

## 💡 实用技巧

**如何加载保存的模型用于实际预测？**

```python
import mlflow.sklearn
import joblib

# 方法1: 通过Run ID加载
model = mlflow.sklearn.load_model("runs:/你的RunID/model")

# 方法2: 如果模型已注册到Model Registry
# model = mlflow.sklearn.load_model("models:/模型名/版本号")

# 加载标准化器（我们在训练时保存的）
scaler = joblib.load("scaler.pkl")  # 注意：实际项目中scaler也应该通过MLFlow加载

# 预测新数据
new_data = [[5.1, 3.5, 1.4, 0.2]]
new_data_scaled = scaler.transform(new_data)
prediction = model.predict(new_data_scaled)
print(f"预测结果: {prediction}")
```

## 🚀 下一步

明天我们将学习如何比较多个实验结果，找出最佳模型！

👉 **明天见： [Day 4 - 比较实验结果](D:\code_workspaces\mlflow-learning\week1\day4\)**
