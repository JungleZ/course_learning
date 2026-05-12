"""
Day 4: FastAPI 接口测试脚本

运行方式：先启动 FastAPI 服务，再运行本脚本
    终端1：python main.py
    终端2：python test_api.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 50)
print("🧪 FastAPI 接口测试")
print("=" * 50)


# 测试1：健康检查
print("\n📌 测试1：健康检查")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   状态码：{response.status_code}")
    print(f"   响应：{json.dumps(response.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"   ❌ 请求失败：{e}")
    print("   请先启动 FastAPI 服务：python main.py")
    exit(1)


# 测试2：单条预测
print("\n📌 测试2：单条预测 - 山鸢尾")
response = requests.post(
    f"{BASE_URL}/predict",
    json={"features": [5.1, 3.5, 1.4, 0.2]}
)
print(f"   状态码：{response.status_code}")
result = response.json()
print(f"   预测结果：{result['prediction']}")
print(f"   置信度：{result['confidence']:.2%}")
print(f"   各类别概率：{result['probabilities']}")


# 测试3：另一条预测
print("\n📌 测试3：单条预测 - 维吉尼亚鸢尾")
response = requests.post(
    f"{BASE_URL}/predict",
    json={"features": [6.7, 3.0, 5.2, 2.3]}
)
result = response.json()
print(f"   预测结果：{result['prediction']}")
print(f"   置信度：{result['confidence']:.2%}")


# 测试4：批量预测
print("\n📌 测试4：批量预测")
response = requests.post(
    f"{BASE_URL}/predict_batch",
    json={"samples": [
        [5.1, 3.5, 1.4, 0.2],
        [6.7, 3.0, 5.2, 2.3],
        [5.9, 3.0, 4.2, 1.5]
    ]}
)
result = response.json()
print(f"   预测数量：{result['count']}")
for i, pred in enumerate(result['predictions']):
    print(f"   样本{i+1}：{pred['prediction']}（置信度 {pred['confidence']:.2%}）")


# 测试5：数据验证（错误输入）
print("\n📌 测试5：数据验证 - 错误输入")
response = requests.post(
    f"{BASE_URL}/predict",
    json={"features": [1.0, 2.0]}  # 只有2个特征，应该4个
)
print(f"   状态码：{response.status_code}")
print(f"   错误信息：{response.json()['detail'][0]['msg']}")


# 测试6：特征值为非数字
print("\n📌 测试6：数据验证 - 非数字输入")
response = requests.post(
    f"{BASE_URL}/predict",
    json={"features": ["abc", 3.5, 1.4, 0.2]}
)
print(f"   状态码：{response.status_code}")
print(f"   错误类型：{response.json()['detail'][0]['type']}")


print("\n" + "=" * 50)
print("✅ 所有测试完成！")
print("💡 试试在浏览器打开 http://127.0.0.1:8000/docs 交互式测试")
