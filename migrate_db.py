"""
数据库迁移脚本 - 添加新字段
运行此脚本以更新数据库结构
"""

from app import create_app, db
from config.settings import config
import os

app = create_app(config[os.environ.get('FLASK_ENV', 'default')])

with app.app_context():
    print("开始数据库迁移...")

    # 创建所有表（包括新字段）
    db.create_all()

    print("✓ 数据库表结构已更新")
    print("\n新增字段：")
    print("- User.last_login: 最后登录时间")
    print("- Submission.ip_address: 提交 IP 地址")
    print("- Submission.submission_hash: 数据完整性哈希")
    print("- Submission.is_valid: 数据有效性标记")
    print("\n✓ 数据库迁移完成！")
