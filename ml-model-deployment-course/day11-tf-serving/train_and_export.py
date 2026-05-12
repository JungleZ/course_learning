"""
Day 11: 训练 Keras 模型并导出为 SavedModel 格式

功能：
1. 训练一个鸢尾花分类模型
2. 导出为 TensorFlow SavedModel 格式
3. 验证导出的模型

运行方式：
    python train_and_export.py
"""

import numpy as np
import os

# ========== 尝试导入 TensorFlow ==========
try:
    import tensorflow as tf
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
except ImportError as e:
    print(f"❌ 缺少依赖：{e}")
    print("请安装：pip install tensorflow scikit-learn")
    exit(1)

print(f"✅ TensorFlow 版本：{tf.__version__}")

# ========== 第1步：加载数据 ==========
print("\n" + "=" * 50)
print("📊 加载鸢尾花数据集")
print("=" * 50)

iris = load_iris()
X = iris.data
y = iris.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"训练集大小：{X_train_scaled.shape[0]}")
print(f"测试集大小：{X_test_scaled.shape[0]}")

# ========== 第2步：构建模型 ==========
print("\n" + "=" * 50)
print("🏗️ 构建 Keras 模型")
print("=" * 50)

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(4,)),
    tf.keras.layers.Dense(16, activation='relu', name='dense_1'),
    tf.keras.layers.Dense(8, activation='relu', name='dense_2'),
    tf.keras.layers.Dense(3, activation='softmax', name='output')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# ========== 第3步：训练模型 ==========
print("\n" + "=" * 50)
print("🏋️ 训练模型")
print("=" * 50)

history = model.fit(
    X_train_scaled, y_train,
    epochs=50,
    batch_size=16,
    validation_split=0.2,
    verbose=1
)

# ========== 第4步：评估模型 ==========
print("\n" + "=" * 50)
print("📈 评估模型")
print("=" * 50)

test_loss, test_accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)
print(f"测试集准确率：{test_accuracy:.2%}")

# ========== 第5步：导出 SavedModel ==========
print("\n" + "=" * 50)
print("💾 导出 SavedModel 格式")
print("=" * 50)

model_dir = os.path.join(os.path.dirname(__file__), "saved_model", "iris_model", "1")
os.makedirs(model_dir, exist_ok=True)

model.save(model_dir)
print(f"✅ 模型已导出到：{model_dir}")

# 验证导出
loaded_model = tf.keras.models.load_model(model_dir)
loaded_loss, loaded_accuracy = loaded_model.evaluate(X_test_scaled, y_test, verbose=0)
print(f"✅ 加载后模型准确率：{loaded_accuracy:.2%}")

# ========== 第6步：测试预测 ==========
print("\n" + "=" * 50)
print("🔮 测试预测")
print("=" * 50)

CLASS_NAMES = ["setosa", "versicolor", "virginica"]

# 预测单条数据
sample = np.array([[5.1, 3.5, 1.4, 0.2]])
sample_scaled = scaler.transform(sample)
prediction = loaded_model.predict(sample_scaled)
predicted_class = np.argmax(prediction, axis=1)[0]

print(f"输入：{sample[0]}")
print(f"预测：{CLASS_NAMES[predicted_class]}")
print(f"概率：{prediction[0]}")

# ========== 第7步：保存预处理参数 ==========
import json

preprocessing_path = os.path.join(os.path.dirname(__file__), "saved_model", "preprocessing.json")
with open(preprocessing_path, 'w') as f:
    json.dump({
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "feature_names": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
        "class_names": CLASS_NAMES
    }, f, indent=2)

print(f"✅ 预处理参数已保存到：{preprocessing_path}")
print("\n🎉 模型训练和导出完成！")
print("下一步：用 Docker 运行 TF Serving")
print("  docker run -d -p 8501:8501 -v <saved_model路径>:/models/iris_model -e MODEL_NAME=iris_model tensorflow/serving")
