"""
更新数据库脚本 - 添加 url_risk_info 和 url_risk_score 字段
"""

from app import create_app, db
from config.settings import config
import os

# 创建应用实例
app = create_app(config[os.environ.get('FLASK_ENV', 'default')])

with app.app_context():
    # 使用 SQLAlchemy 的 op 来添加列
    from sqlalchemy import inspect
    
    # 检查表是否存在
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'submissions' in tables:
        # 使用原生 SQL 添加列
        from sqlalchemy import text
        
        # 检查列是否已存在
        columns = [col['name'] for col in inspector.get_columns('submissions')]
        
        if 'url_risk_info' not in columns:
            db.session.execute(text('ALTER TABLE submissions ADD COLUMN url_risk_info TEXT'))
            print("✓ 添加 url_risk_info 列成功")
        
        if 'url_risk_score' not in columns:
            db.session.execute(text('ALTER TABLE submissions ADD COLUMN url_risk_score INTEGER'))
            print("✓ 添加 url_risk_score 列成功")
        
        db.session.commit()
        print("\n数据库更新完成！")
    else:
        print("数据库表不存在，请先运行 init_db.py")
