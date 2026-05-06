import os
import sys
import numpy as np

# 添加路径以便导入模型
sys.path.append(os.path.abspath('../../week6-large-scale/movie-rating'))

def load_fraud_model():
    """加载欺诈检测模型"""
    try:
        import joblib
        model_path = '../../week6-large-scale/credit-fraud/model/review_classifier.pkl'
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            return model
    except Exception as e:
        print(f"加载欺诈检测模型失败: {e}")
    return None

# 初始化模型
_fraud_model = load_fraud_model()

def calculate_fraud_risk(user_data):
    """计算用户欺诈风险分数"""
    if not _fraud_model:
        return 0.1  # 默认低风险

    # 构造特征（模拟信用卡欺诈检测的特征）
    features = np.array([[
        user_data.get('activity_score', 0.5),
        user_data.get('profile_completeness', 0.5),
        user_data.get('message_frequency', 0.5),
        user_data.get('report_count', 0),
        1.0 if user_data.get('verified_email') else 0.0,
        user_data.get('account_age_days', 1) / 365.0,
        user_data.get('matches_count', 0) / 100.0,
        len(user_data.get('bio', '')),
        len(user_data.get('interests', [])),
        user_data.get('photo_count', 0)
    ]]).reshape(1, -1)

    # 预测风险概率
    try:
        prob = _fraud_model.predict_proba(features)[0]
        return float(prob[1])  # 返回欺诈概率
    except:
        return 0.1

def check_message_fraud(message, sentiment_score):
    """检查消息是否涉嫌欺诈"""
    fraud_keywords = ['money', 'transfer', 'bank', 'urgent', 'investment',
                     '钱', '转账', '银行', '紧急', '投资', '中奖']

    message_lower = message.lower()

    # 高风险关键词
    for keyword in fraud_keywords:
        if keyword in message_lower:
            return True, 0.8

    # 结合情感分析（过于积极的可能是机器人）
    if sentiment_score > 0.95:
        return True, 0.6

    return False, 0.0

if __name__ == '__main__':
    # 测试
    test_user = {
        'activity_score': 0.3,
        'profile_completeness': 0.4,
        'message_frequency': 0.2,
        'verified_email': False,
        'account_age_days': 2,
        'matches_count': 0,
        'bio': '',
        'interests': [],
        'photo_count': 0
    }

    risk = calculate_fraud_risk(test_user)
    print(f"欺诈风险分数: {risk:.3f}")

    is_fraud, score = check_message_fraud("Hi, I want to transfer money to you!", 0.99)
    print(f"消息欺诈检测: {is_fraud}, 分数: {score}")
