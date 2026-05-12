# Day 2：模型保存与加载

## 🎯 今日目标
1. 理解为什么要保存模型
2. 学会用不同格式保存模型
3. 学会加载已保存的模型做预测

---

## 🤔 为什么要保存模型？

想象一下：
- 你花了一整天训练了一个模型 ⏰
- 关掉电脑后，模型消失了 💨
- 下次要用又得重新训练 😭

**保存模型 = 把训练成果存到硬盘上，随时可以加载使用！**

---

## 📦 常见的模型保存格式

| 格式 | 库 | 适用场景 | 文件大小 |
|------|------|----------|----------|
| pickle | Python 内置 | sklearn 模型 | 较大 |
| joblib | sklearn 自带 | sklearn 模型（推荐） | 较小，大数据更高效 |
| .pt/.pth | PyTorch | PyTorch 模型 | 中等 |
| .h5/.keras | TensorFlow/Keras | TF 模型 | 中等 |
| ONNX (.onnx) | ONNX | 跨框架部署 | 小，推理快 |
| SavedModel | TensorFlow | TF Serving 部署 | 中等 |

---

## 🏃 运行代码

```bash
cd day02-save-load
python save_load_model.py
```

你会看到：
1. 训练模型 → 保存到文件 → 从文件加载 → 用加载的模型做预测
2. 不同格式的保存/加载方式

---

## 🔑 关键概念

### 序列化（Serialization）
= 把内存中的 Python 对象 → 变成文件存到硬盘

### 反序列化（Deserialization）
= 把硬盘上的文件 → 读回内存变成 Python 对象

---

## ⚠️ 安全提示
- 不要加载来自不信任来源的 pickle/joblib 文件
- 它们可以执行任意 Python 代码（安全风险）
- 生产环境中考虑使用 ONNX 等更安全的格式

---

## ✅ 今日检查清单
- [ ] 理解模型保存的意义
- [ ] 成功用 joblib 保存 sklearn 模型
- [ ] 成功加载模型并用它做预测
- [ ] 了解不同保存格式的区别

## 🎉 完成 Day 2！明天我们学习用 Flask 把模型变成 API 服务。
