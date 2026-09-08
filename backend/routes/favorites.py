from flask import Blueprint, request, jsonify
from sjk import get_connection
from routes.users import verify_token

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/', methods=['GET'])
def get_favorites():
    spot_id = request.args.get('spot_id')
    keyword = request.args.get('keyword', '')
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        if spot_id:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM spot_favorites 
                WHERE spot_id = %s
            """, (spot_id,))
            result = cursor.fetchone()
            
            auth_header = request.headers.get('Authorization')
            user_id = None
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                payload = verify_token(token)
                if payload:
                    user_id = payload['user_id']
            
            is_favorited = False
            if user_id:
                cursor.execute("""
                    SELECT id FROM spot_favorites 
                    WHERE spot_id = %s AND user_id = %s
                """, (spot_id, user_id))
                user_result = cursor.fetchone()
                if user_result:
                    is_favorited = True
            
            return jsonify({
                'success': True, 
                'data': {
                    'count': result['count'] if result['count'] else 0,
                    'is_favorited': is_favorited
                }
            })
        else:
            query = """
                SELECT f.*, s.name as spot_name, u.username
                FROM spot_favorites f
                JOIN spots s ON f.spot_id = s.id
                JOIN users u ON f.user_id = u.id
            """
            params = []
            
            if keyword:
                query += " WHERE s.name LIKE %s"
                params.append(f'%{keyword}%')
            
            query += " ORDER BY f.created_at DESC"
            
            cursor.execute(query, params)
            favorites = cursor.fetchall()
            
            return jsonify({'success': True, 'data': favorites})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@favorites_bp.route('/', methods=['POST'])
def add_favorite():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'success': False, 'message': '登录已过期'}), 401
    
    data = request.get_json()
    spot_id = data.get('spot_id')
    
    if not spot_id:
        return jsonify({'success': False, 'message': '景点ID不能为空'}), 400
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO spot_favorites (spot_id, user_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE created_at = CURRENT_TIMESTAMP
        """, (spot_id, payload['user_id']))
        conn.commit()
        
        return jsonify({'success': True, 'message': '收藏成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@favorites_bp.route('/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
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
        cursor.execute("SELECT * FROM spot_favorites WHERE id = %s", (favorite_id,))
        favorite = cursor.fetchone()
        
        if not favorite:
            return jsonify({'success': False, 'message': '收藏不存在'}), 404
        
        if payload['role'] != 'admin' and favorite['user_id'] != payload['user_id']:
            return jsonify({'success': False, 'message': '无权限删除'}), 403
        
        cursor.execute("DELETE FROM spot_favorites WHERE id = %s", (favorite_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': '取消收藏成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@favorites_bp.route('/remove/<int:spot_id>', methods=['DELETE'])
def remove_favorite_by_spot(spot_id):
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
        cursor = conn.cursor()
        cursor.execute("DELETE FROM spot_favorites WHERE spot_id = %s AND user_id = %s", (spot_id, payload['user_id']))
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': '取消收藏成功'})
        else:
            return jsonify({'success': False, 'message': '收藏不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()