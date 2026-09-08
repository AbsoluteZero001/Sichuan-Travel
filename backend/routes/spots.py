from flask import Blueprint, request, jsonify
from sjk import get_connection
from routes.users import verify_token
import json

spots_bp = Blueprint('spots', __name__)

@spots_bp.route('/<int:spot_id>', methods=['GET'])
def get_spot(spot_id):
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM spots WHERE id = %s", (spot_id,))
        spot = cursor.fetchone()
        
        if not spot:
            return jsonify({'success': False, 'message': '景点不存在'}), 404
        
        spot_dict = dict(spot)
        if spot_dict.get('images'):
            try:
                spot_dict['images'] = json.loads(spot_dict['images'])
            except:
                spot_dict['images'] = []
        
        return jsonify({'success': True, 'data': spot_dict})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@spots_bp.route('/<int:spot_id>', methods=['PUT'])
def update_spot(spot_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'success': False, 'message': '登录已过期'}), 401
    
    if payload['role'] != 'admin':
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    
    data = request.get_json()
    name = data.get('name')
    city = data.get('city')
    
    if not name or not city:
        return jsonify({'success': False, 'message': '景点名称和城市不能为空'}), 400
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM spots WHERE id = %s", (spot_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '景点不存在'}), 404
        
        images_data = data.get('images', [])
        if isinstance(images_data, list):
            images_json = json.dumps(images_data)
        else:
            images_json = '[]'
        
        cursor.execute("""
            UPDATE spots SET name=%s, city=%s, season=%s, price=%s, open_time=%s, image=%s, images=%s, description=%s, guide=%s, tips=%s
            WHERE id = %s
        """, (
            name,
            city,
            data.get('season', ''),
            data.get('price', 0),
            data.get('open_time', ''),
            data.get('image', ''),
            images_json,
            data.get('description', ''),
            data.get('guide', ''),
            data.get('tips', ''),
            spot_id
        ))
        conn.commit()
        
        return jsonify({'success': True, 'message': '景点更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@spots_bp.route('/<int:spot_id>', methods=['DELETE'])
def delete_spot(spot_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'success': False, 'message': '登录已过期'}), 401
    
    if payload['role'] != 'admin':
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM spots WHERE id = %s", (spot_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '景点不存在'}), 404
        
        cursor.execute("DELETE FROM spots WHERE id = %s", (spot_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': '景点删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()