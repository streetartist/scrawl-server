from flask import Flask, request, jsonify
from utils.db import get_db, validate_api_key, update_project_access_time
from sqlalchemy import text  # 添加这行导入
import time

app = Flask(__name__)

@app.route('/api/<project_id>/set', methods=['POST'])
def set_variable(project_id):
    api_key = request.headers.get('X-API-Key')
    if not api_key or not validate_api_key(project_id, api_key):
        return jsonify({'error': 'Invalid API key'}), 401
    
    data = request.get_json()
    var_name = data.get('var_name')
    var_value = data.get('var_value')
    
    if not var_name or var_value is None:
        return jsonify({'error': 'Missing var_name or var_value'}), 400
    
    # 更新项目访问时间
    update_project_access_time(project_id)
    
    db = get_db()
    current_time = time.time()
    
    try:
        # 插入或更新变量
        db.execute(
            text("""
                INSERT INTO variables (project_id, var_name, var_value, last_updated)
                VALUES (:project_id, :var_name, :var_value, :last_updated)
                ON CONFLICT (project_id, var_name) 
                DO UPDATE SET var_value = EXCLUDED.var_value, last_updated = EXCLUDED.last_updated
            """),
            {
                "project_id": project_id,
                "var_name": var_name,
                "var_value": str(var_value),
                "last_updated": current_time
            }
        )
        db.commit()
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
