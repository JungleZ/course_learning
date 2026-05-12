"""
Day 12: 将 sklearn 模型转换为 ONNX 格式

功能：
1. 训练 sklearn 模型
2. 转换为 ONNX 格式
3. 验证转换结果

运行方式：
    python convert_to_onnx.py
"""

import numpy as np
import os

print("=" * 50)
print("📦 ONNX 模型转换演示")
print("=" * 50)

# ========== 第1步：训练 sklearn 模型 ==========
print("\n🏋️ 第1步：训练 sklearn 模型")

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

# 决策树模型
dt_model = DecisionTreeClassifier(max_depth=3, random_state=42)
dt_model.fit(X_train, y_train)
dt_accuracy = accuracy_score(y_test, dt_model.predict(X_test))
print(f"   决策树准确率：{dt_accuracy:.2%}")

# 随机森林模型
rf_model = RandomForestClassifier(n_estimators=10, random_state=42)
rf_model.fit(X_train, y_train)
rf_accuracy = accuracy_score(y_test, rf_model.predict(X_test))
print(f"   随机森林准确率：{rf_accuracy:.2%}")


# ========== 第2步：转换为 ONNX ==========
print("\n🔄 第2步：转换为 ONNX 格式")

try:
    import skl2onnx
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
except ImportError:
    print("❌ 请安装 skl2onnx：pip install skl2onnx")
    exit(1)

# 定义输入类型
initial_type = [('float_input', FloatTensorType([None, 4]))]

# 转换决策树
dt_onnx = convert_sklearn(dt_model, initial_types=initial_type)
dt_onnx_path = os.path.join(os.path.dirname(__file__), "decision_tree.onnx")
with open(dt_onnx_path, "wb") as f:
    f.write(dt_onnx.SerializeToString())
print(f"✅ 决策树已转换为 ONNX：{dt_onnx_path}")

# 转换随机森林
rf_onnx = convert_sklearn(rf_model, initial_types=initial_type)
rf_onnx_path = os.path.join(os.path.dirname(__file__), "random_forest.onnx")
with open(rf_onnx_path, "wb") as f:
    f.write(rf_onnx.SerializeToString())
print(f"✅ 随机森林已转换为 ONNX：{rf_onnx_path}")


# ========== 第3步：验证 ONNX 模型 ==========
print("\n✅ 第3步：验证 ONNX 模型")

try:
    import onnx
    import onnxruntime as ort
except ImportError:
    print("❌ 请安装 onnx 和 onnxruntime：pip install onnx onnxruntime")
    exit(1)

# 验证模型格式
onnx_model = onnx.load(dt_onnx_path)
onnx.checker.check_model(onnx_model)
print("✅ ONNX 模型格式验证通过")

# 用 ONNX Runtime 推理
sess = ort.InferenceSession(dt_onnx_path)
input_name = sess.get_inputs()[0].name
output_names = [output.name for output in sess.get_outputs()]

print(f"   输入名称：{input_name}")
print(f"   输出名称：{output_names}")

# 测试推理
test_data = X_test[:5].astype(np.float32)
onnx_results = sess.run(None, {input_name: test_data})

print(f"\n📊 对比推理结果：")
print(f"{'样本':<6} {'sklearn':<12} {'ONNX':<12} {'一致？'}")
print(f"{'-'*6} {'-'*12} {'-'*12} {'-'*6}")

sklearn_preds = dt_model.predict(X_test[:5])
onnx_preds = onnx_results[0]

for i in range(5):
    match = "✅" if sklearn_preds[i] == onnx_preds[i] else "❌"
    print(f"{i+1:<6} {sklearn_preds[i]:<12} {onnx_preds[i]:<12} {match}")

# 概率对比
if len(onnx_results) > 1:
    sklearn_probs = dt_model.predict_proba(X_test[:5])
    onnx_probs = onnx_results[1]
    print(f"\n📊 概率对比（第一个样本）：")
    print(f"   sklearn: {sklearn_probs[0]}")
    print(f"   ONNX:    {onnx_probs[0]}")


# ========== 第4步：PyTorch 转 ONNX ==========
print("\n" + "=" * 50)
print("🔄 PyTorch 模型转 ONNX")
print("=" * 50)

try:
    import torch
    import torch.nn as nn
    
    class SimpleNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1 = nn.Linear(4, 16)
            self.relu = nn.ReLU()
            self.fc2 = nn.Linear(16, 3)
        
        def forward(self, x):
            return self.fc2(self.relu(self.fc1(x)))
    
    # 训练
    torch_model = SimpleNet()
    X_train_t = torch.FloatTensor(X_train)
    y_train_t = torch.LongTensor(y_train)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(torch_model.parameters(), lr=0.01)
    
    for epoch in range(200):
        optimizer.zero_grad()
        outputs = torch_model(X_train_t)
        loss = criterion(outputs, y_train_t)
        loss.backward()
        optimizer.step()
    
    torch_model.eval()
    
    # 导出 ONNX
    pytorch_onnx_path = os.path.join(os.path.dirname(__file__), "pytorch_model.onnx")
    dummy_input = torch.randn(1, 4)
    
    torch.onnx.export(
        torch_model,
        dummy_input,
        pytorch_onnx_path,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
        opset_version=11
    )
    print(f"✅ PyTorch 模型已导出 ONNX：{pytorch_onnx_path}")
    
    # 验证
    ort_sess = ort.InferenceSession(pytorch_onnx_path)
    test_input = X_test[:3].astype(np.float32)
    ort_output = ort_sess.run(None, {"input": test_input})
    
    torch_output = torch_model(torch.FloatTensor(test_input)).detach().numpy()
    
    print(f"   PyTorch 输出：{np.argmax(torch_output, axis=1)}")
    print(f"   ONNX 输出：   {np.argmax(ort_output[0], axis=1)}")
    print(f"   结果一致？   {'✅ 是' if np.allclose(torch_output, ort_output[0], atol=1e-5) else '❌ 否'}")

except ImportError:
    print("⚠️ PyTorch 未安装，跳过 PyTorch 转 ONNX 演示")


# ========== 第5步：文件大小对比 ==========
print("\n" + "=" * 50)
print("📊 文件大小对比")
print("=" * 50)

import joblib
import tempfile

# 保存 sklearn 格式
with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
    joblib.dump(dt_model, f.name)
    sklearn_size = os.path.getsize(f.name)
    os.unlink(f.name)

onnx_size = os.path.getsize(dt_onnx_path)

print(f"{'格式':<20} {'大小':<15} {'说明'}")
print(f"{'-'*20} {'-'*15} {'-'*30}")
print(f"{'sklearn (joblib)':<20} {sklearn_size:<15,} {'Python 专用'}")
print(f"{'ONNX':<20} {onnx_size:<15,} {'跨平台通用'}")

if onnx_size < sklearn_size:
    ratio = (1 - onnx_size/sklearn_size) * 100
    print(f"\n💡 ONNX 比 sklearn 小 {ratio:.1f}%")

print("\n🎉 模型转换完成！")
print("下一步：运行 onnx_inference.py 测试 ONNX Runtime 推理")
