"""
Day 2: 模型保存与加载 - 不同格式演示

演示内容：
1. 用 joblib 保存/加载 sklearn 模型
2. 用 torch.save 保存/加载 PyTorch 模型
3. 对比不同保存格式
"""

# ========== 第1步：导入库 ==========
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib  # sklearn 推荐的模型保存工具
import os
import numpy as np

# ========== 第2步：训练一个 sklearn 模型 ==========
print("=" * 50)
print("📦 模型保存与加载演示")
print("=" * 50)

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)

# 原始模型准确率
y_pred = model.predict(X_test)
original_accuracy = accuracy_score(y_test, y_pred)
print(f"📊 原始模型准确率：{original_accuracy:.2%}")


# ========== 第3步：用 joblib 保存模型 ==========
print("\n--- 方式1：joblib（sklearn推荐） ---")

joblib_path = "model_joblib.pkl"
joblib.dump(model, joblib_path)
print(f"✅ 模型已保存到 {joblib_path}")
print(f"   文件大小：{os.path.getsize(joblib_path)} 字节")

# 加载模型
loaded_model_joblib = joblib.load(joblib_path)
y_pred_loaded = loaded_model_joblib.predict(X_test)
loaded_accuracy = accuracy_score(y_test, y_pred_loaded)
print(f"✅ 加载后模型准确率：{loaded_accuracy:.2%}")
print(f"   准确率一致？{'✅ 是' if original_accuracy == loaded_accuracy else '❌ 否'}")


# ========== 第4步：用 pickle 保存模型 ==========
print("\n--- 方式2：pickle（Python内置） ---")

import pickle

pickle_path = "model_pickle.pkl"
with open(pickle_path, 'wb') as f:
    pickle.dump(model, f)
print(f"✅ 模型已保存到 {pickle_path}")
print(f"   文件大小：{os.path.getsize(pickle_path)} 字节")

with open(pickle_path, 'rb') as f:
    loaded_model_pickle = pickle.load(f)

y_pred_pickle = loaded_model_pickle.predict(X_test)
pickle_accuracy = accuracy_score(y_test, y_pred_pickle)
print(f"✅ 加载后模型准确率：{pickle_accuracy:.2%}")


# ========== 第5步：保存模型+预处理 ==========
print("\n--- 方式3：保存完整管道（模型+预处理） ---")

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# 创建包含预处理和模型的管道
pipeline = Pipeline([
    ('scaler', StandardScaler()),          # 标准化
    ('classifier', DecisionTreeClassifier(max_depth=3, random_state=42))
])

pipeline.fit(X_train, y_train)
pipeline_path = "model_pipeline.pkl"
joblib.dump(pipeline, pipeline_path)
print(f"✅ 完整管道已保存到 {pipeline_path}")

loaded_pipeline = joblib.load(pipeline_path)
y_pred_pipeline = loaded_pipeline.predict(X_test)
print(f"✅ 加载后管道准确率：{accuracy_score(y_test, y_pred_pipeline):.2%}")

# 管道的好处：预测时自动做标准化，不需要手动处理
new_data = np.array([[5.1, 3.5, 1.4, 0.2]])
pred = loaded_pipeline.predict(new_data)
print(f"🔮 新数据预测：{iris.target_names[pred[0]]}")


# ========== 第6步：PyTorch 模型保存 ==========
print("\n" + "=" * 50)
print("--- 方式4：PyTorch 模型保存 ---")
print("=" * 50)

try:
    import torch
    import torch.nn as nn

    # 定义一个简单的 PyTorch 模型
    class SimpleNet(nn.Module):
        def __init__(self):
            super(SimpleNet, self).__init__()
            self.fc1 = nn.Linear(4, 16)
            self.relu = nn.ReLU()
            self.fc2 = nn.Linear(16, 3)

        def forward(self, x):
            x = self.relu(self.fc1(x))
            x = self.fc2(x)
            return x

    # 训练 PyTorch 模型
    torch_model = SimpleNet()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(torch_model.parameters(), lr=0.01)

    X_train_torch = torch.FloatTensor(X_train)
    y_train_torch = torch.LongTensor(y_train)

    # 简单训练 100 轮
    for epoch in range(100):
        optimizer.zero_grad()
        outputs = torch_model(X_train_torch)
        loss = criterion(outputs, y_train_torch)
        loss.backward()
        optimizer.step()

    print(f"✅ PyTorch 模型训练完成")

    # 方式A：保存模型权重（推荐）
    weights_path = "pytorch_model_weights.pth"
    torch.save(torch_model.state_dict(), weights_path)
    print(f"✅ 模型权重已保存到 {weights_path}")

    # 加载权重
    loaded_torch_model = SimpleNet()
    loaded_torch_model.load_state_dict(torch.load(weights_path))
    loaded_torch_model.eval()
    print(f"✅ 模型权重已加载")

    # 方式B：保存完整模型（不推荐，但最简单）
    full_path = "pytorch_model_full.pth"
    torch.save(torch_model, full_path)
    print(f"✅ 完整模型已保存到 {full_path}")

    loaded_full = torch.load(full_path)
    loaded_full.eval()
    print(f"✅ 完整模型已加载")

    # 验证 PyTorch 模型预测
    with torch.no_grad():
        test_output = loaded_torch_model(torch.FloatTensor(X_test[:5]))
        _, predicted = torch.max(test_output, 1)
        print(f"🔮 PyTorch 模型预测前5个样本：{predicted.numpy()}")
        print(f"   实际标签：{y_test[:5]}")

except ImportError:
    print("⚠️ PyTorch 未安装，跳过 PyTorch 保存演示")
    print("   安装命令：pip install torch")


# ========== 第7步：格式对比总结 ==========
print("\n" + "=" * 50)
print("📊 模型保存格式对比总结")
print("=" * 50)
print(f"{'格式':<15} {'文件大小':<15} {'适用场景'}")
print(f"{'-'*15} {'-'*15} {'-'*30}")
print(f"{'joblib (.pkl)':<15} {os.path.getsize(joblib_path):<15} {'sklearn 模型（推荐）'}")
print(f"{'pickle (.pkl)':<15} {os.path.getsize(pickle_path):<15} {'Python 通用'}")
if os.path.exists("pytorch_model_weights.pth"):
    print(f"{'PyTorch权重':<15} {os.path.getsize('pytorch_model_weights.pth'):<15} {'PyTorch 模型（推荐）'}")
    print(f"{'PyTorch完整':<15} {os.path.getsize('pytorch_model_full.pth'):<15} {'PyTorch 模型（简单但不推荐）'}")

# 清理生成的文件
for f in [joblib_path, pickle_path, pipeline_path, 
          "pytorch_model_weights.pth", "pytorch_model_full.pth"]:
    if os.path.exists(f):
        os.remove(f)
        print(f"🗑️ 已清理临时文件：{f}")

print("\n🎉 模型保存与加载演示完成！")
