# Day 12：ONNX 模型优化与部署

## 🎯 今日目标
1. 理解 ONNX 的作用和优势
2. 将 sklearn 和 PyTorch 模型转换为 ONNX 格式
3. 用 ONNX Runtime 进行高性能推理
4. 了解跨平台部署的优势

---

## 🤔 什么是 ONNX？

ONNX = Open Neural Network Exchange（开放神经网络交换格式）

| 优势 | 说明 |
|------|------|
| **跨框架** | PyTorch → ONNX → TensorFlow，模型自由转换 |
| **高性能** | ONNX Runtime 比 PyTorch 推理快 2-5 倍 |
| **跨平台** | Windows/Linux/Mac/Android/iOS/Web |
| **小体积** | 模型文件更小，推理更快 |
| **安全** | 不执行任意代码（不像 pickle） |

### 为什么要用 ONNX？

```
训练（PyTorch/TensorFlow/sklearn）
         ↓
    转换为 ONNX
         ↓
推理（ONNX Runtime）→ 更快、更小、跨平台
```

---

## 📁 项目结构

```
day12-onnx/
├── guide.md              # 本文件
├── convert_to_onnx.py    # 模型转换脚本
└── onnx_inference.py     # ONNX 推理脚本
```

---

## 🚀 运行步骤

### 第1步：安装依赖
```bash
pip install onnx onnxruntime skl2onnx scikit-learn
```

### 第2步：转换模型
```bash
cd day12-onnx
python convert_to_onnx.py
```

会将 sklearn 模型转换为 ONNX 格式。

### 第3步：ONNX 推理
```bash
python onnx_inference.py
```

---

## 🔑 关键概念

### ONNX 模型结构
```
model.onnx
├── Graph (计算图)
│   ├── Nodes (算子节点)
│   ├── Inputs (输入)
│   └── Outputs (输出)
└── Opset (算子版本)
```

### ONNX Runtime
- 微软开源的高性能推理引擎
- 支持 CPU/GPU
- 比 PyTorch 推理快 2-5 倍
- 支持 C++/Python/C#/Java/JavaScript

### 性能对比

| 推理方式 | 速度 | 内存 | 跨平台 |
|----------|------|------|--------|
| sklearn (joblib) | 慢 | 大 | ❌ 仅 Python |
| PyTorch (.pth) | 中等 | 中 | ❌ 需 PyTorch |
| **ONNX Runtime** | **快** | **小** | ✅ 全平台 |

---

## 📊 ONNX 在不同平台的部署

| 平台 | ONNX Runtime 版本 | 用途 |
|------|-------------------|------|
| Windows/Linux | ONNX Runtime | 服务端推理 |
| Android | ONNX Runtime Mobile | 移动端推理 |
| iOS | ONNX Runtime Mobile | 移动端推理 |
| Web | ONNX Runtime Web | 浏览器推理 |
| 边缘设备 | ONNX Runtime Mobile | IoT 设备 |

---

## 💡 高级优化

### 量化（Quantization）
```python
from onnxruntime.quantization import quantize_dynamic, QuantType

quantize_dynamic(
    model_input="model.onnx",
    model_output="model_quantized.onnx",
    weight_type=QuantType.QUInt8  # 8位量化
)
```
量化后模型更小、推理更快，精度损失很小。

### 图优化
```python
from onnxruntime import InferenceSession
from onnxruntime.transformers import optimizer

optimized_model = optimizer.optimize_model("model.onnx")
optimized_model.save_model_to_file("model_optimized.onnx")
```

---

## ✅ 今日检查清单
- [ ] 安装 ONNX 相关依赖
- [ ] 成功将 sklearn 模型转换为 ONNX
- [ ] 用 ONNX Runtime 进行推理
- [ ] 对比 ONNX 与原始模型的推理结果
- [ ] 了解 ONNX 跨平台部署的优势

## 🎉 完成 Day 12！明天学习移动端部署。
