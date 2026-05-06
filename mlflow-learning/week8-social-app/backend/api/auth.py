import os
import sqlite3
import hashlib
import jwt
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# 计算数据库绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'users.db')
print(f"DEBUG auth.py: Using database at {DB_PATH}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'error': '请填写所有字段'}), 400

    if len(password) < 6:
        return jsonify({'error': '密码至少6位'}), 400

    password_hash = hash_password(password)
    print(f"DEBUG Register: username={username}, hash={password_hash[:20]}...")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                     (username, email, password_hash))
        conn.commit()
        user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        return jsonify({'message': '注册成功', 'user_id': user_id}), 201
    except sqlite3.IntegrityError as e:
        if 'username' in str(e):
            return jsonify({'error': '用户名已存在'}), 400
        else:
            return jsonify({'error': '邮箱已注册'}), 400
    finally:
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    print(f"DEBUG Login: username={username}, password length={len(password) if password else 0}")

    if not all([username, password]):
        return jsonify({'error': '请填写用户名和密码'}), 400;

    password_hash = hash_password(password)
    print(f"DEBUG Login: computed hash={password_hash[:30]}...")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # 先检查用户是否存在
    check = conn.execute('SELECT id, username, password_hash FROM users WHERE username = ?',
                      (username,)).fetchone()
    if check:
        print(f"DEBUG: Found user id={check['id']}, stored hash={check['password_hash'][:30]}...")
        print(f"DEBUG: Hash match: {check['password_hash'] == password_hash}")
    else:
        print(f"DEBUG: User {username} NOT FOUND in database!")
        conn.close()
        return jsonify({'error': '用户名或密码错误'}), 401;

    user = conn.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?',
                      (username, password_hash)).fetchone()
    print(f"DEBUG: Login query result: {user}")
    conn.close()

    if not user:
        print(f"DEBUG: Login failed - password hash doesn't match!")
        return jsonify({'error': '用户名或密码错误'}), 401;

    # 集成欺诈检测
    try:
        import sys
        ml_dir = os.path.join(os.path.dirname(DB_PATH), 'ml')
        if ml_dir not in sys.path:
            sys.path.append(ml_dir)
        from fraud import calculate_fraud_risk, check_message_fraud
        user_data = {
            'activity_score': user['activity_score'] if 'activity_score' in user.keys() else 0.5,
            'profile_completeness': 0.5,
            'message_frequency': 0.5,
            'verified_email': '@' in user['email'],
            'account_age_days': 1,
            'matches_count': 0,
            'bio': user['bio'],
            'interests': user['interests'],
            'photo_count': 1 if user['avatar_url'] else 0
        }
        fraud_score = calculate_fraud_risk(user_data)
        print(f"DEBUG: Fraud risk score: {fraud_score:.3f}")
        
        if fraud_score > 0.7:
            return jsonify({'error': '账户存在风险，请联系客服'}), 403;
    except Exception as e:
        print(f"欺诈检测失败: {e}")

    token = generate_token(user['id'])
    return jsonify({
        'message': '登录成功',
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email']
        }
    })

@auth_bp.route('/verify', methods=['GET'])
def verify():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({'error': '未登录'}), 401;

    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        user = conn.execute('SELECT id, username, email FROM users WHERE id = ?', (payload['user_id'],)).fetchone()
        conn.close()

        if not user:
            return jsonify({'error': '用户不存在'}), 401;

        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        })
    except:
        return jsonify({'error': '登录已过期'}), 401;
