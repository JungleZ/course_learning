"""
Day 3: 训练并保存模型（供 Flask API 使用）
"""

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib

# 训练模型
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"📊 模型准确率：{accuracy:.2%}")

# 保存模型
joblib.dump(model, "iris_model.pkl")
print("✅ 模型已保存到 iris_model.pkl")
