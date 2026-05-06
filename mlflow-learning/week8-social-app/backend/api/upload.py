import os
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

# 头像保存目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AVATAR_DIR = os.path.join(BASE_DIR, 'frontend', 'avatars')
os.makedirs(AVATAR_DIR, exist_ok=True)

def verify_token(request):
    from flask import current_app
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    try:
        import jwt
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

@upload_bp.route('/avatar', methods=['POST'])
def upload_avatar():
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': '未登录'}), 401;

    if 'avatar' not in request.files:
        return jsonify({'error': '请上传图片'}), 400;

    file = request.files['avatar']
    if not file.filename:
        return jsonify({'error': '文件无效'}), 400;

    # 检查文件类型
    allowed = ['.jpg', '.jpeg', '.png', '.gif']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        return jsonify({'error': '只支持 JPG/PNG/GIF 格式'}), 400;

    # 保存文件
    filename = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)
    file.save(filepath)

    # 更新数据库
    import sqlite3
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'users.db'))
    conn.row_factory = sqlite3.Row
    conn.execute('UPDATE users SET avatar_url = ? WHERE id = ?', (filename, user_id))
    conn.commit()
    conn.close()

    return jsonify({
        'message': '上传成功',
        'avatar_url': filename
    }), 201;

@upload_bp.route('/avatar/<filename>', methods=['GET'])
def get_avatar(filename):
    return send_file(os.path.join(AVATAR_DIR, filename))
