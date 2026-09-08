from flask import Blueprint, request, jsonify
import jwt
from sjk import get_connection
from datetime import datetime, timedelta

users_bp = Blueprint('users', __name__)
SECRET_KEY = 'sichuan_tourism_secret_key'

def generate_token(user_id, username, role):
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@users_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')", (username, password))
        conn.commit()
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        token = generate_token(user[0], user[1], user[3])
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'token': token,
            'user': {'id': user[0], 'username': user[1], 'role': user[3]}
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@users_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        token = generate_token(user[0], user[1], user[3])
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'user': {'id': user[0], 'username': user[1], 'role': user[3]}
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@users_bp.route('/my-favorites', methods=['GET'])
def get_my_favorites():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'success': False, 'message': '登录已过期'}), 401
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT f.*, s.name as spot_name, s.image as spot_image
            FROM spot_favorites f
            JOIN spots s ON f.spot_id = s.id
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC
        """, (payload['user_id'],))
        favorites = cursor.fetchall()
        
        return jsonify({'success': True, 'data': favorites})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@users_bp.route('/change-password', methods=['POST'])
def change_password():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'success': False, 'message': '登录已过期'}), 401
    
    data = request.get_json()
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')
    
    if not old_password or not new_password:
        return jsonify({'success': False, 'message': '请填写所有密码字段'}), 400
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (payload['user_id'],))
        user = cursor.fetchone()
        
        if not user or user[2] != old_password:
            return jsonify({'success': False, 'message': '旧密码错误'}), 400
        
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, payload['user_id']))
        conn.commit()
        
        return jsonify({'success': True, 'message': '密码修改成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()