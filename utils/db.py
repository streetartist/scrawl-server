import os
from sqlalchemy import create_engine, text, exc
from sqlalchemy.orm import scoped_session, sessionmaker
import uuid
import time

# 从环境变量获取数据库连接字符串（使用您提供的格式）
DATABASE_URL = os.getenv('DATABASE_URL')

# 创建数据库引擎（使用连接池参数）
engine = create_engine(
    DATABASE_URL,
    pool_size=5,           # 连接池大小
    max_overflow=10,       # 允许的最大连接数（pool_size + max_overflow）
    pool_recycle=300,      # 连接回收时间（秒）
    pool_pre_ping=True     # 每次使用前检查连接是否有效
)

db_session = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
))

def init_db():
    """初始化数据库（如果表不存在则创建）"""
    try:
        # 创建项目表
        db_session.execute(text("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id VARCHAR(255) PRIMARY KEY,
                project_name VARCHAR(255) NOT NULL,
                created_at DOUBLE PRECISION NOT NULL,
                last_accessed DOUBLE PRECISION NOT NULL,
                api_key VARCHAR(255) NOT NULL
            )
        """))
        
        # 创建变量表
        db_session.execute(text("""
            CREATE TABLE IF NOT EXISTS variables (
                project_id VARCHAR(255) NOT NULL,
                var_name VARCHAR(255) NOT NULL,
                var_value TEXT NOT NULL,
                last_updated DOUBLE PRECISION NOT NULL,
                PRIMARY KEY (project_id, var_name),
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """))
        
        db_session.commit()
        print("Database tables created successfully")
    except exc.SQLAlchemyError as e:
        print(f"Error initializing database: {str(e)}")
        db_session.rollback()

def get_db():
    """获取数据库会话"""
    return db_session

def validate_api_key(project_id, api_key):
    """验证API密钥"""
    try:
        result = db_session.execute(
            text("""
                SELECT api_key FROM projects 
                WHERE project_id = :project_id AND api_key = :api_key
            """),
            {"project_id": project_id, "api_key": api_key}
        ).fetchone()
        
        return result is not None
    except exc.SQLAlchemyError:
        return False

def generate_api_key():
    """生成API密钥"""
    return str(uuid.uuid4())

def update_project_access_time(project_id):
    """更新项目访问时间"""
    try:
        db_session.execute(
            text("""
                UPDATE projects SET last_accessed = :last_accessed 
                WHERE project_id = :project_id
            """),
            {"last_accessed": time.time(), "project_id": project_id}
        )
        db_session.commit()
    except exc.SQLAlchemyError:
        db_session.rollback()
