from flask import Flask, request, jsonify
from utils.db import get_db, validate_api_key, update_project_access_time
from sqlalchemy import text  # 添加这行导入

app = Flask(__name__)

@app.route('/api/<project_id>/all', methods=['GET'])
def get_all_variables(project_id):
    api_key = request.headers.get('X-API-Key')
    if not api_key or not validate_api_key(project_id, api_key):
        return jsonify({'error': 'Invalid API key'}), 401
    
    # 更新项目访问时间
    update_project_access_time(project_id)
    
    db = get_db()
    
    try:
        # 获取所有变量
        results = db.execute(
            text("""
                SELECT var_name, var_value, last_updated FROM variables 
                WHERE project_id = :project_id
            """),
            {"project_id": project_id}
        ).fetchall()
        
        variables = {}
        for row in results:
            variables[row[0]] = {
                'value': row[1],
                'last_updated': row[2]
            }
        
        return jsonify(variables), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
