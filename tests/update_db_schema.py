"""
直接更新数据库结构的脚本
使用 SQLAlchemy 的 ALTER TABLE 添加新字段
"""

from app import create_app, db
from config.settings import config
import os

app = create_app(config[os.environ.get('FLASK_ENV', 'default')])

with app.app_context():
    print("开始手动更新数据库结构...")

    # 获取数据库连接
    connection = db.engine.connect()

    try:
        # 为 users 表添加 last_login 字段
        print("\n1. 更新 users 表...")
        try:
            connection.execute(db.text(
                "ALTER TABLE users ADD COLUMN last_login DATETIME"
            ))
            print("   ✓ 添加 last_login 字段成功")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ last_login 字段已存在")
            else:
                raise

        # 为 submissions 表添加新字段
        print("\n2. 更新 submissions 表...")

        # 添加 ip_address 字段
        try:
            connection.execute(db.text(
                "ALTER TABLE submissions ADD COLUMN ip_address VARCHAR(50)"
            ))
            print("   ✓ 添加 ip_address 字段成功")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ ip_address 字段已存在")
            else:
                raise

        # 添加 submission_hash 字段
        try:
            connection.execute(db.text(
                "ALTER TABLE submissions ADD COLUMN submission_hash VARCHAR(64)"
            ))
            print("   ✓ 添加 submission_hash 字段成功")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ submission_hash 字段已存在")
            else:
                raise

        # 添加 is_valid 字段
        try:
            connection.execute(db.text(
                "ALTER TABLE submissions ADD COLUMN is_valid BOOLEAN DEFAULT 1"
            ))
            print("   ✓ 添加 is_valid 字段成功")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ is_valid 字段已存在")
            else:
                raise

        # 提交事务
        connection.commit()

        print("\n" + "=" * 60)
        print("✓ 数据库结构更新完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 更新失败：{str(e)}")
        connection.rollback()
    finally:
        connection.close()
