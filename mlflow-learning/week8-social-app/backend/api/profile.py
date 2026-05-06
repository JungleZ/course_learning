import os
import sqlite3
import json
import jwt
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

profile_bp = Blueprint('profile', __name__)

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

PROFILE_FIELDS = [
    'id', 'username', 'email', 'gender', 'birthday', 'bio', 'interests',
    'location', 'avatar_url', 'dating_goal', 'about_me', 'know_me',
    'ideal_type', 'free_time_hobbies', 'love_vision', 'meeting_preference',
    'mbti', 'wechat', 'real_name_verified', 'avatar_verified',
    'marital_status_verified', 'marital_status'
]

@profile_bp.route('/me', methods=['GET'])
def get_profile():
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': '未登录'}), 401

    conn = get_db()
    cols = ', '.join(PROFILE_FIELDS)
    user = conn.execute(f'SELECT {cols} FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if not user:
        return jsonify({'error': '用户不存在'}), 404

    return jsonify(dict(user))

@profile_bp.route('/update', methods=['POST'])
def update_profile():
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': '未登录'}), 401

    data = request.get_json()

    updatable = [
        'gender', 'birthday', 'bio', 'interests', 'location', 'avatar_url',
        'dating_goal', 'about_me', 'know_me', 'ideal_type', 'free_time_hobbies',
        'love_vision', 'meeting_preference', 'mbti', 'wechat', 'marital_status'
    ]

    set_parts = []
    values = []
    for field in updatable:
        val = data.get(field)
        if val is not None:
            set_parts.append(f"{field} = ?")
            values.append(val if field != 'interests' else json.dumps(val, ensure_ascii=False))

    if not set_parts:
        return jsonify({'message': '没有需要更新的字段'})

    values.append(user_id)

    conn = get_db()
    conn.execute(f"UPDATE users SET {', '.join(set_parts)} WHERE id = ?", values)
    conn.commit()
    conn.close()

    return jsonify({'message': '更新成功'})

@profile_bp.route('/<int:user_id>', methods=['GET'])
def view_profile(user_id):
    conn = get_db()
    cols = ', '.join(PROFILE_FIELDS)
    user = conn.execute(f'SELECT {cols} FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if not user:
        return jsonify({'error': '用户不存在'}), 404

    return jsonify(dict(user))

@profile_bp.route('/visit/<int:user_id>', methods=['POST'])
def record_visit(user_id):
    visitor_id = verify_token(request)
    if not visitor_id:
        return jsonify({'error': '未登录'}), 401
    if visitor_id == user_id:
        return jsonify({'message': 'ok'})

    conn = get_db()
    conn.execute(
        "INSERT INTO profile_visits (visitor_id, visited_user_id) VALUES (?, ?)",
        (visitor_id, user_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'ok'})

@profile_bp.route('/visitors', methods=['GET'])
def get_visitors():
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': '未登录'}), 401

    conn = get_db()
    rows = conn.execute('''
        SELECT DISTINCT v.visitor_id, u.username, u.avatar_url, MAX(v.visited_at) as last_visit
        FROM profile_visits v
        JOIN users u ON u.id = v.visitor_id
        WHERE v.visited_user_id = ?
        GROUP BY v.visitor_id
        ORDER BY last_visit DESC
        LIMIT 20
    ''', (user_id,)).fetchall()

    result = []
    for r in rows:
        result.append({
            'visitor_id': r['visitor_id'],
            'username': r['username'],
            'avatar_url': r['avatar_url'],
            'last_visit': r['last_visit']
        })

    conn.close()
    return jsonify({'visitors': result, 'total': len(result)})
