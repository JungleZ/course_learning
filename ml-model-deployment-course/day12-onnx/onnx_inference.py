"""
Day 12: ONNX Runtime 推理演示

功能：
1. 加载 ONNX 模型
2. 高性能推理
3. 对比不同推理方式的性能

运行方式：
    python onnx_inference.py
"""

import numpy as np
import time
import os

print("=" * 50)
print("🚀 ONNX Runtime 推理演示")
print("=" * 50)

# ========== 检查 ONNX 模型文件 ==========
onnx_path = os.path.join(os.path.dirname(__file__), "decision_tree.onnx")
if not os.path.exists(onnx_path):
    print("❌ ONNX 模型文件不存在！请先运行 convert_to_onnx.py")
    exit(1)

# ========== 第1步：加载 ONNX 模型 ==========
print("\n📦 加载 ONNX 模型")

import onnxruntime as ort

# 创建推理会话
sess = ort.InferenceSession(onnx_path)

# 查看模型信息
input_info = sess.get_inputs()[0]
output_info = sess.get_outputs()

print(f"   输入名称：{input_info.name}")
print(f"   输入形状：{input_info.shape}")
print(f"   输入类型：{input_info.type}")
print(f"   输出数量：{len(output_info)}")
for i, out in enumerate(output_info):
    print(f"   输出{i}：{out.name} {out.shape} {out.type}")


# ========== 第2步：单条推理 ==========
print("\n🔮 单条推理")

from sklearn.datasets import load_iris
iris = load_iris()
CLASS_NAMES = iris.target_names

# 准备输入数据
test_data = np.array([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)

# 推理
results = sess.run(None, {input_info.name: test_data})

prediction = results[0][0]
print(f"   输入：{test_data[0]}")
print(f"   预测类别：{CLASS_NAMES[prediction]}")

if len(results) > 1:
    probabilities = results[1][0]
    print(f"   各类别概率：")
    for i, (name, prob) in enumerate(zip(CLASS_NAMES, probabilities)):
        print(f"     {name}: {prob:.4f}")


# ========== 第3步：批量推理 ==========
print("\n📦 批量推理")

batch_data = iris.data[:10].astype(np.float32)
results = sess.run(None, {input_info.name: batch_data})

print(f"   批量预测 {len(batch_data)} 条数据：")
for i, pred in enumerate(results[0]):
    print(f"     样本{i+1}：{CLASS_NAMES[pred]}")


# ========== 第4步：性能对比 ==========
print("\n" + "=" * 50)
print("⏱️ 性能对比：ONNX Runtime vs sklearn")
print("=" * 50)

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import joblib

# 准备数据
X = iris.data.astype(np.float32)
y = iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# sklearn 模型
sk_model = DecisionTreeClassifier(max_depth=3, random_state=42)
sk_model.fit(X_train, y_train)

# 测试数据
test_samples = X_test.astype(np.float32)
n_iterations = 1000

# sklearn 推理
start = time.time()
for _ in range(n_iterations):
    sk_model.predict(test_samples)
sklearn_time = time.time() - start

# ONNX Runtime 推理
start = time.time()
for _ in range(n_iterations):
    sess.run(None, {input_info.name: test_samples})
onnx_time = time.time() - start

print(f"\n   推理 {n_iterations} 次，{len(test_samples)} 条/次")
print(f"   sklearn 耗时：{sklearn_time:.3f} 秒")
print(f"   ONNX Runtime 耗时：{onnx_time:.3f} 秒")
if onnx_time < sklearn_time:
    speedup = sklearn_time / onnx_time
    print(f"   🚀 ONNX Runtime 快 {speedup:.2f} 倍！")
else:
    print(f"   ℹ️ 简单模型（如决策树）ONNX 优势不明显")
    print(f"   复杂模型（如神经网络）ONNX 通常快 2-5 倍")


# ========== 第5步：ONNX Runtime 高级功能 ==========
print("\n" + "=" * 50)
print("🔧 ONNX Runtime 高级功能")
print("=" * 50)

# 1. 线程控制
sess_optimized = ort.InferenceSession(
    onnx_path,
    sess_options=ort.SessionOptions()
)
# 设置线程数
opts = ort.SessionOptions()
opts.intra_op_num_threads = 4
opts.inter_op_num_threads = 1

# 2. GPU 支持（如果有 CUDA）
providers = ort.get_available_providers()
print(f"   可用的执行提供者：{providers}")
print(f"   {'✅ CUDA 可用' if 'CUDAExecutionProvider' in providers else '⚠️ 仅 CPU 模式'}")


# ========== 第6步：模拟部署场景 ==========
print("\n" + "=" * 50)
print("🌐 模拟 API 部署场景")
print("=" * 50)

def onnx_predict(features):
    """模拟 ONNX Runtime 部署的预测函数"""
    input_data = np.array([features], dtype=np.float32)
    results = sess.run(None, {input_info.name: input_data})
    
    prediction = results[0][0]
    if len(results) > 1:
        probs = results[1][0]
        return {
            "prediction": CLASS_NAMES[prediction],
            "probabilities": {CLASS_NAMES[i]: float(probs[i]) for i in range(3)}
        }
    return {"prediction": CLASS_NAMES[prediction]}

# 测试
result = onnx_predict([5.1, 3.5, 1.4, 0.2])
print(f"   预测结果：{result}")

print("\n🎉 ONNX Runtime 推理演示完成！")
print("💡 总结：ONNX Runtime 适合需要高性能、跨平台部署的场景")
