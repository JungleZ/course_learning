"""
Day 1: 训练你的第一个机器学习模型 - 鸢尾花分类

这个脚本会：
1. 加载鸢尾花数据集
2. 训练一个决策树分类模型
3. 评估模型准确率
4. 用模型做预测

小白友好：每一行都有详细中文注释！
"""

# ========== 第1步：导入需要的库 ==========

# sklearn 是机器学习最常用的库
from sklearn.datasets import load_iris          # 鸢尾花数据集
from sklearn.model_selection import train_test_split  # 切分训练/测试集
from sklearn.tree import DecisionTreeClassifier       # 决策树分类器
from sklearn.metrics import accuracy_score, classification_report  # 评估指标

import numpy as np  # 数值计算库


# ========== 第2步：加载数据 ==========
print("=" * 50)
print("🌺 鸢尾花分类模型训练")
print("=" * 50)

# load_iris() 返回一个数据对象
iris = load_iris()

# X 是特征（花的测量数据）：花萼长度、花萼宽度、花瓣长度、花瓣宽度
X = iris.data
print(f"\n📊 数据形状：{X.shape}")  # (150, 4) 表示 150 条数据，每条 4 个特征
print(f"特征名称：{iris.feature_names}")

# y 是标签（花的品种）：0=山鸢尾, 1=变色鸢尾, 2=维吉尼亚鸢尾
y = iris.target
print(f"标签类别：{iris.target_names}")
print(f"各类别数量：山鸢尾={sum(y==0)}, 变色鸢尾={sum(y==1)}, 维吉尼亚鸢尾={sum(y==2)}")


# ========== 第3步：切分训练集和测试集 ==========
# 训练集：用来训练模型（就像学生做练习题）
# 测试集：用来检验模型（就像学生考试）
# test_size=0.2 表示 80% 训练，20% 测试
# random_state=42 保证每次运行结果一样（可复现）

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n✂️ 数据切分：")
print(f"  训练集大小：{X_train.shape[0]} 条")
print(f"  测试集大小：{X_test.shape[0]} 条")


# ========== 第4步：创建并训练模型 ==========
# DecisionTreeClassifier 是决策树分类器
# max_depth=3 限制树的最大深度（防止过拟合）

model = DecisionTreeClassifier(max_depth=3, random_state=42)

# 训练模型！fit = 拟合 = 学习
print(f"\n🏋️ 开始训练决策树模型...")
model.fit(X_train, y_train)
print(f"✅ 训练完成！")


# ========== 第5步：评估模型 ==========
# 用测试集来检验模型学得好不好

# 预测测试集
y_pred = model.predict(X_test)

# 计算准确率
accuracy = accuracy_score(y_test, y_pred)
print(f"\n📈 模型准确率：{accuracy:.2%}")

# 详细分类报告
print(f"\n📋 详细分类报告：")
print(classification_report(y_test, y_pred, target_names=iris.target_names))


# ========== 第6步：用模型做预测 ==========
print("=" * 50)
print("🔮 使用模型进行预测")
print("=" * 50)

# 假设我们在花园里量了一朵花：
# 花萼长度=5.1cm, 花萼宽度=3.5cm, 花瓣长度=1.4cm, 花瓣宽度=0.2cm
new_flower = np.array([[5.1, 3.5, 1.4, 0.2]])

prediction = model.predict(new_flower)
predicted_species = iris.target_names[prediction[0]]

print(f"\n🌸 新花朵的测量数据：")
print(f"  花萼长度: 5.1cm")
print(f"  花萼宽度: 3.5cm")
print(f"  花瓣长度: 1.4cm")
print(f"  花瓣宽度: 0.2cm")
print(f"\n🎯 预测结果：这朵花是【{predicted_species}】！")

# 再试一朵
new_flower2 = np.array([[6.7, 3.0, 5.2, 2.3]])
prediction2 = model.predict(new_flower2)
predicted_species2 = iris.target_names[prediction2[0]]

print(f"\n🌸 另一朵花的测量数据：")
print(f"  花萼长度: 6.7cm")
print(f"  花萼宽度: 3.0cm")
print(f"  花瓣长度: 5.2cm")
print(f"  花瓣宽度: 2.3cm")
print(f"\n🎯 预测结果：这朵花是【{predicted_species2}】！")


# ========== 第7步：查看模型学到了什么 ==========
print("\n" + "=" * 50)
print("🌳 决策树学到的规则（简化版）：")
print("=" * 50)

from sklearn.tree import export_text
tree_rules = export_text(model, feature_names=iris.feature_names)
print(tree_rules)

print("\n💡 解读：模型通过花瓣长度和宽度来判断花的品种，非常直观！")
print("🎉 恭喜！你已经训练并使用了第一个机器学习模型！")
