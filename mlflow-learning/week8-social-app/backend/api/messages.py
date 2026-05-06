import os
import sys
import sqlite3
import jwt
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

messages_bp = Blueprint('messages', __name__)

# 数据库路径（统一）
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

@messages_bp.route('/send', methods=['POST'])
def send_message():
    sender_id = verify_token(request)
    if not sender_id:
        return jsonify({'error': '未登录'}), 401;

    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content')

    if not all([receiver_id, content]):
        return jsonify({'error': '请填写完整信息'}), 400;

    if sender_id == receiver_id:
        return jsonify({'error': '不能给自己发消息'}), 400;

    # 情感分析
    sentiment_score = 0.5
    try:
        # 使用正确的导入路径
        ml_dir = os.path.abspath(os.path.join(BASE_DIR, '..', 'ml'))
        if ml_dir not in sys.path:
            sys.path.append(ml_dir)
        from sentiment import analyze_sentiment
        result = analyze_sentiment(content)
        sentiment_score = result['score']
    except Exception as e:
        print(f"情感分析失败: {e}")

    conn = get_db()
    conn.execute('INSERT INTO messages (sender_id, receiver_id, content, sentiment_score) VALUES (?, ?, ?, ?)',
                  (sender_id, receiver_id, content, sentiment_score))
    conn.commit()
    message_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()

    return jsonify({
        'message': '发送成功',
        'message_id': message_id,
        'sentiment_score': sentiment_score
    }), 201

@messages_bp.route('/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    """获取与指定用户的聊天记录"""
    current_user_id = verify_token(request)
    if not current_user_id:
        return jsonify({'error': '未登录'}), 401;
    
    conn = get_db()
    messages = conn.execute('''SELECT m.*, 
                             u1.username as sender_name,
                             u2.username as receiver_name
                      FROM messages m
                      JOIN users u1 ON u1.id = m.sender_id
                      JOIN users u2 ON u2.id = m.receiver_id
                      WHERE (m.sender_id = ? AND m.receiver_id = ?) 
                         OR (m.sender_id = ? AND m.receiver_id = ?)
                      ORDER BY m.created_at''',
                     (current_user_id, user_id, user_id, current_user_id)).fetchall()
    conn.close()
    
    result = []
    for msg in messages:
        result.append({
            'id': msg['id'],
            'sender_id': msg['sender_id'],
            'sender_name': msg['sender_name'],
            'receiver_id': msg['receiver_id'],
            'receiver_name': msg['receiver_name'],
            'content': msg['content'],
            'sentiment_score': msg['sentiment_score'],
            'created_at': msg['created_at']
        })
    
    return jsonify({'messages': result})


@messages_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """获取互相匹配的用户会话列表"""
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': '未登录'}), 401

    conn = get_db()
    rows = conn.execute('''
        SELECT other_user.id as other_id, other_user.username, other_user.avatar_url,
               latest_msg.content, latest_msg.created_at, latest_msg.sender_id
        FROM matches mt
        JOIN users other_user ON (
            (mt.user1_id = ? AND other_user.id = mt.user2_id)
            OR (mt.user2_id = ? AND other_user.id = mt.user1_id)
        )
        LEFT JOIN (
            SELECT
                CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END as other_id2,
                MAX(id) as max_id
            FROM messages
            WHERE sender_id = ? OR receiver_id = ?
            GROUP BY other_id2
        ) conv ON conv.other_id2 = other_user.id
        LEFT JOIN messages latest_msg ON latest_msg.id = conv.max_id
        WHERE mt.status = 'matched' AND other_user.id != ?
        ORDER BY latest_msg.created_at DESC
    ''', (user_id, user_id, user_id, user_id, user_id, user_id)).fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            'id': r['other_id'],
            'username': r['username'],
            'avatar_url': r['avatar_url'],
            'last_message': r['content'],
            'last_time': r['created_at'],
            'last_sender_id': r['sender_id']
        })

    return jsonify({'conversations': result})
