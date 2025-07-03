from flask import Flask, request, jsonify
from utils.db import get_db, validate_api_key, update_project_access_time
from sqlalchemy import text  # 添加这行导入

app = Flask(__name__)

@app.route('/api/<project_id>/get', methods=['GET'])
def get_variable(project_id):
    api_key = request.headers.get('X-API-Key')
    if not api_key or not validate_api_key(project_id, api_key):
        return jsonify({'error': 'Invalid API key'}), 401
    
    var_name = request.args.get('var_name')
    if not var_name:
        return jsonify({'error': 'Missing var_name'}), 400
    
    # 更新项目访问时间
    update_project_access_time(project_id)
    
    db = get_db()
    
    try:
        # 获取变量值
        result = db.execute(
            text("""
                SELECT var_value, last_updated FROM variables 
                WHERE project_id = :project_id AND var_name = :var_name
            """),
            {"project_id": project_id, "var_name": var_name}
        ).fetchone()
        
        if not result:
            return jsonify({'error': 'Variable not found'}), 404
        
        return jsonify({
            'var_value': result[0],
            'last_updated': result[1]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
