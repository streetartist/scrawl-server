from flask import Flask, request, jsonify
from utils.db import get_db
import time
import os

app = Flask(__name__)

@app.route('/api/cleanup', methods=['POST'])
def cleanup_expired_projects():
    # 验证管理员密钥
    admin_key = request.headers.get('X-Admin-Key')
    if admin_key != os.getenv('ADMIN_KEY', 'default-secret'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    db = get_db()
    
    try:
        # 删除超过90天未访问的项目
        threshold = time.time() - (90 * 24 * 60 * 60)
        
        # 首先删除关联的变量
        db.execute(
            text("""
                DELETE FROM variables 
                WHERE project_id IN (
                    SELECT project_id FROM projects 
                    WHERE last_accessed < :threshold
                )
            """),
            {"threshold": threshold}
        )
        
        # 然后删除项目
        result = db.execute(
            text("""
                DELETE FROM projects 
                WHERE last_accessed < :threshold
                RETURNING project_id
            """),
            {"threshold": threshold}
        )
        
        deleted_count = len(result.fetchall())
        db.commit()
        
        return jsonify({
            'status': 'success',
            'projects_deleted': deleted_count
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
