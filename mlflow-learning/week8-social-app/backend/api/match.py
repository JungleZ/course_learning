import os
import sqlite3
import json
import jwt
import numpy as np
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

match_bp = Blueprint('match', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'users.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def verify_token(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def calculate_compatibility(user1, user2):
    """计算两个用户的匹配度"""
    score = 0.0

    # 性别匹配（异性相吸）
    if user1['gender'] and user2['gender']:
        if user1['gender'] != user2['gender']:
            score += 0.3
        else:
            score += 0.1

    # 地理位置
    if user1['location'] and user2['location']:
        if user1['location'] == user2['location']:
            score += 0.2
        else:
            score += 0.05

    # 兴趣相似度
    if user1['interests'] and user2['interests']:
        try:
            interests1 = json.loads(user1['interests']) if isinstance(user1['interests'], str) else user1['interests']
            interests2 = json.loads(user2['interests']) if isinstance(user2['interests'], str) else user2['interests']
            if isinstance(interests1, (list, tuple)) and isinstance(interests2, (list, tuple)):
                common = len(set(interests1) & set(interests2))
                total = len(set(interests1) | set(interests2))
                score += 0.3 * (common / total if total > 0 else 0)
        except:
            score += 0

    # 随机因素（模拟ML模型）
    score += np.random.uniform(0, 0.2)

    return min(score, 1.0)

@match_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': '未登录'}), 401

    conn = get_db()
    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if not current_user:
        conn.close()
        return jsonify({'error': '用户不存在'}), 404

    # 获取所有其他用户
    all_users = conn.execute('SELECT * FROM users WHERE id != ?', (user_id,)).fetchall()

    # 获取当前用户已经喜欢的人列表
    liked_ids = set()
    liked_rows = conn.execute(
        "SELECT user2_id FROM matches WHERE user1_id = ? AND status IN ('liked','matched')",
        (user_id,)
    ).fetchall()
    for r in liked_rows:
        liked_ids.add(r['user2_id'])
    # 也检查 user2_id = current 的记录
    liked_rows2 = conn.execute(
        "SELECT user1_id FROM matches WHERE user2_id = ? AND status IN ('liked','matched')",
        (user_id,)
    ).fetchall()
    for r in liked_rows2:
        liked_ids.add(r['user1_id'])

    conn.close()

    recommendations = []
    for user in all_users:
        score = calculate_compatibility(current_user, user)
        recommendations.append({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'gender': user['gender'],
                'bio': user['bio'],
                'interests': user['interests'],
                'location': user['location'],
                'avatar_url': user['avatar_url'],
                'mbti': user['mbti'],
                'about_me': user['about_me'],
                'ideal_type': user['ideal_type'],
                'dating_goal': user['dating_goal'],
                'free_time_hobbies': user['free_time_hobbies'],
                'love_vision': user['love_vision'],
                'meeting_preference': user['meeting_preference'],
                'marital_status': user['marital_status'],
                'real_name_verified': user['real_name_verified'],
                'avatar_verified': user['avatar_verified'],
                'marital_status_verified': user['marital_status_verified']
            },
            'compatibility_score': round(score, 3),
            'already_liked': user['id'] in liked_ids
        })

    # 按匹配度排序
    recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)

    return jsonify({
        'recommendations': recommendations[:20]  # 返回前20个推荐
    })

@match_bp.route('/like/<int:user_id>', methods=['POST'])
def like_user(user_id):
    current_user_id = verify_token(request)
    if not current_user_id:
        return jsonify({'error': '未登录'}), 401

    if current_user_id == user_id:
        return jsonify({'error': '不能喜欢自己'}), 400

    conn = get_db()

    # 检查是否已经匹配过
    existing = conn.execute('SELECT * FROM matches WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)',
                          (current_user_id, user_id, user_id, current_user_id)).fetchone()

    if existing:
        conn.close()
        return jsonify({'error': '已经操作过该用户'}), 400

    # 计算匹配度
    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (current_user_id,)).fetchone()
    target_user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if not target_user:
        conn.close()
        return jsonify({'error': '用户不存在'}), 404

    score = calculate_compatibility(current_user, target_user)

    # 创建匹配记录
    conn.execute('INSERT INTO matches (user1_id, user2_id, compatibility_score, status) VALUES (?, ?, ?, ?)',
                  (current_user_id, user_id, score, 'liked'))
    conn.commit()

    # 检查对方是否也喜欢了自己（互相喜欢）
    match = conn.execute('SELECT * FROM matches WHERE user1_id = ? AND user2_id = ? AND status = "liked"',
                       (user_id, current_user_id)).fetchone()

    if match:
        # 互相喜欢，更新状态为matched
        conn.execute('UPDATE matches SET status = "matched" WHERE id = ?', (match['id'],))
        conn.execute('UPDATE matches SET status = "matched" WHERE user1_id = ? AND user2_id = ?',
                      (current_user_id, user_id))
        conn.commit()
        conn.close()
        return jsonify({'message': '恭喜！互相喜欢！', 'matched': True})

    conn.close()
    return jsonify({'message': '已发送喜欢', 'matched': False})

@match_bp.route('/matches', methods=['GET'])
def get_matches():
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': '未登录'}), 401

    conn = get_db()
    matches = conn.execute('''SELECT m.*, u.id as matched_user_id, u.username, u.avatar_url
                             FROM matches m
                             JOIN users u ON (u.id = m.user1_id OR u.id = m.user2_id)
                             WHERE (m.user1_id = ? OR m.user2_id = ?) AND m.status = "matched"
                             AND u.id != ?''',
                            (user_id, user_id, user_id)).fetchall()
    conn.close()

    result = []
    for m in matches:
        # 获取最后一条消息
        conn2 = get_db()
        last_msg = conn2.execute('''SELECT content, created_at, sender_id
                                   FROM messages
                                   WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
                                   ORDER BY created_at DESC LIMIT 1''',
                                  (user_id, m['matched_user_id'], m['matched_user_id'], user_id)).fetchone()
        conn2.close()

        last_message = ''
        last_time = ''
        if last_msg:
            last_message = last_msg['content']
            last_time = last_msg['created_at']
            last_sender_id = last_msg['sender_id']
        else:
            last_sender_id = None

        result.append({
            'match_id': m['id'],
            'user': {
                'id': m['matched_user_id'],
                'username': m['username'],
                'avatar_url': m['avatar_url']
            },
            'compatibility_score': m['compatibility_score'],
            'created_at': m['created_at'],
            'last_message': last_message,
            'last_time': last_time,
            'last_sender_id': last_sender_id
        })

    return jsonify({'matches': result})

@match_bp.route('/stats', methods=['GET'])
def get_stats():
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': '未登录'}), 401

    conn = get_db()

    # 我喜欢的人
    liked_by_me = conn.execute(
        "SELECT COUNT(*) FROM matches WHERE user1_id = ? AND status IN ('liked','matched')",
        (user_id,)
    ).fetchone()[0]

    # 喜欢我的人
    liked_me = conn.execute(
        "SELECT COUNT(*) FROM matches WHERE user2_id = ? AND status IN ('liked','matched')",
        (user_id,)
    ).fetchone()[0]

    # 互相匹配
    matched = conn.execute(
        "SELECT COUNT(*) FROM matches WHERE (user1_id = ? OR user2_id = ?) AND status = 'matched'",
        (user_id, user_id)
    ).fetchone()[0]

    conn.close()

    return jsonify({
        'liked_by_me': liked_by_me,
        'liked_me': liked_me,
        'matched': matched
    })


@match_bp.route('/liked-by-me', methods=['GET'])
def get_liked_by_me():
    """获取我喜欢的用户列表"""
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': '未登录'}), 401

    conn = get_db()
    rows = conn.execute('''
        SELECT m.user2_id as target_id, u.username, u.avatar_url, u.gender, u.bio, u.location,
               m.compatibility_score, m.status, m.created_at
        FROM matches m
        JOIN users u ON u.id = m.user2_id
        WHERE m.user1_id = ? AND m.status IN ('liked','matched')
        ORDER BY m.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            'id': r['target_id'],
            'username': r['username'],
            'avatar_url': r['avatar_url'],
            'gender': r['gender'],
            'bio': r['bio'],
            'location': r['location'],
            'compatibility_score': r['compatibility_score'],
            'status': r['status'],
            'created_at': r['created_at']
        })

    return jsonify({'users': result, 'total': len(result)})


@match_bp.route('/liked-me', methods=['GET'])
def get_liked_me():
    """获取喜欢我的用户列表"""
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': '未登录'}), 401

    conn = get_db()
    rows = conn.execute('''
        SELECT m.user1_id as target_id, u.username, u.avatar_url, u.gender, u.bio, u.location,
               m.compatibility_score, m.status, m.created_at
        FROM matches m
        JOIN users u ON u.id = m.user1_id
        WHERE m.user2_id = ? AND m.status IN ('liked','matched')
        ORDER BY m.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            'id': r['target_id'],
            'username': r['username'],
            'avatar_url': r['avatar_url'],
            'gender': r['gender'],
            'bio': r['bio'],
            'location': r['location'],
            'compatibility_score': r['status'] == 'matched',
            'status': r['status'],
            'created_at': r['created_at']
        })

    return jsonify({'users': result, 'total': len(result)})