import os
import sqlite3
import jwt
import hashlib
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# 配置
SECRET_KEY = "social_app_secret_key_2026"
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=7)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.db')
print(f"DEBUG: Database path: {DB_PATH}")

# 数据库初始化
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  gender TEXT,
                  birthday TEXT,
                  bio TEXT,
                  interests TEXT,
                  location TEXT,
                  avatar_url TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS matches
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user1_id INTEGER,
                  user2_id INTEGER,
                  compatibility_score REAL,
                  status TEXT DEFAULT 'pending',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user1_id) REFERENCES users(id),
                  FOREIGN KEY(user2_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sender_id INTEGER,
                  receiver_id INTEGER,
                  content TEXT NOT NULL,
                  sentiment_score REAL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(sender_id) REFERENCES users(id),
                  FOREIGN KEY(receiver_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

init_db()

# 工具函数
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

# 路由
@app.route('/')
def home():
    return send_file('../frontend/index.html')

@app.route('/test')
def test():
    return jsonify({"message": "test ok"})

# 导入API路由
from api.auth import auth_bp
from api.profile import profile_bp
from api.match import match_bp
from api.messages import messages_bp
from api.upload import upload_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(profile_bp, url_prefix='/api/profile')
app.register_blueprint(match_bp, url_prefix='/api/match')
app.register_blueprint(messages_bp, url_prefix='/api/messages')
app.register_blueprint(upload_bp, url_prefix='/api/upload')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("交友App后端已启动!")
    print("访问: http://localhost:5052")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5052, debug=True)