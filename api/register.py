from flask import Flask, request, jsonify
from utils.db import get_db, generate_api_key, init_db
import uuid
import time

app = Flask(__name__)

@app.route('/api/register', methods=['POST'])
def register_project():
    # 确保数据库已初始化
    init_db()
    
    data = request.get_json()
    project_name = data.get('project_name')
    
    if not project_name:
        return jsonify({'error': 'Missing project_name'}), 400
    
    db = get_db()
    project_id = str(uuid.uuid4())
    api_key = generate_api_key()
    created_at = time.time()
    
    try:
        # 插入新项目
        db.execute(
            text("""
                INSERT INTO projects (project_id, project_name, created_at, last_accessed, api_key)
                VALUES (:project_id, :project_name, :created_at, :created_at, :api_key)
            """),
            {
                "project_id": project_id,
                "project_name": project_name,
                "created_at": created_at,
                "api_key": api_key
            }
        )
        db.commit()
        
        return jsonify({
            'project_id': project_id,
            'api_key': api_key
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
