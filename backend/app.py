from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from routes.users import users_bp, verify_token
from routes.spots import spots_bp
from routes.favorites import favorites_bp
from routes.ai import ai_bp
from sjk import init_db, get_connection
import os
import json

app = Flask(__name__)
CORS(app, origins='*')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(spots_bp, url_prefix='/api/spots')
app.register_blueprint(favorites_bp, url_prefix='/api/favorites')
app.register_blueprint(ai_bp, url_prefix='/api/ai')

@app.route('/api/spots/', methods=['GET'])
@app.route('/api/spots', methods=['GET'])
def get_spots():
    keyword = request.args.get('keyword', '')
    season = request.args.get('season', '')
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT s.*, COALESCE(f.favorite_count, 0) as favorite_count
            FROM spots s
            LEFT JOIN (
                SELECT spot_id, COUNT(*) as favorite_count
                FROM spot_favorites
                GROUP BY spot_id
            ) f ON s.id = f.spot_id
            WHERE 1=1
        """
        params = []
        
        if keyword:
            query += " AND (s.name LIKE %s OR s.city LIKE %s OR s.season LIKE %s)"
            params.append(f'%{keyword}%')
            params.append(f'%{keyword}%')
            params.append(f'%{keyword}%')
        
        if season:
            query += " AND s.season = %s"
            params.append(season)
        
        query += " ORDER BY f.favorite_count DESC, s.id ASC"
        
        cursor.execute(query, params)
        spots = cursor.fetchall()
        
        result_spots = []
        for spot in spots:
            spot_dict = dict(spot)
            if spot_dict.get('images'):
                try:
                    spot_dict['images'] = json.loads(spot_dict['images'])
                except:
                    spot_dict['images'] = []
            
            result_spots.append(spot_dict)
        
        return jsonify({'success': True, 'data': result_spots})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/index.html')
def index_html():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/about-sichuan.html')
def about_sichuan():
    return send_from_directory(FRONTEND_DIR, 'about-sichuan.html')

@app.route('/all-spots.html')
def all_spots():
    return send_from_directory(FRONTEND_DIR, 'all-spots.html')

@app.route('/spot-detail.html')
def spot_detail():
    return send_from_directory(FRONTEND_DIR, 'spot-detail.html')

@app.route('/travel-tips.html')
def travel_tips():
    return send_from_directory(FRONTEND_DIR, 'travel-tips.html')

@app.route('/login.html')
def login():
    return send_from_directory(FRONTEND_DIR, 'login.html')

@app.route('/register.html')
def register():
    return send_from_directory(FRONTEND_DIR, 'register.html')

@app.route('/admin-panel.html')
def admin_panel():
    return send_from_directory(FRONTEND_DIR, 'admin-panel.html')

@app.route('/user-profile.html')
def user_profile():
    return send_from_directory(FRONTEND_DIR, 'user-profile.html')

@app.route('/common.js')
def common_js():
    return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), 'common.js')

@app.route('/style.css')
def style_css():
    return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), 'style.css')

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'images'), filename)

@app.route('/api/upload', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'}), 400
        
        if file:
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                import uuid
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file.save(os.path.join(FRONTEND_DIR, 'images', filename))
                return jsonify({
                    'success': True,
                    'url': f'/images/{filename}'
                })
            else:
                return jsonify({'success': False, 'message': '不支持的文件格式，支持png、jpg、jpeg、gif'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/images', methods=['GET'])
def list_images():
    try:
        images_dir = os.path.join(FRONTEND_DIR, 'images')
        if not os.path.exists(images_dir):
            return jsonify({'success': True, 'images': []})
        
        images = []
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append({
                    'filename': filename,
                    'url': f'/images/{filename}'
                })
        
        return jsonify({'success': True, 'images': images})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/images/<filename>', methods=['DELETE'])
def delete_image(filename):
    try:
        image_path = os.path.join(FRONTEND_DIR, 'images', filename)
        if os.path.exists(image_path):
            os.remove(image_path)
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            return jsonify({'success': False, 'message': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=3000, debug=False)
