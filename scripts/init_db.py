"""
数据库初始化脚本
创建数据库表并添加测试用户
"""

from app import create_app, db
from config.settings import config
import os

# 创建应用实例
app = create_app(config[os.environ.get('FLASK_ENV', 'default')])

with app.app_context():
    # 创建所有数据库表
    db.create_all()
    print("✓ 数据库表创建成功")

    # 创建测试用户
    from app.models.user import User

    # 检查是否已存在管理员账户
    admin = User.get_by_student_id('12345678')
    if not admin:
        admin = User.create_user(
            student_id='12345678',
            password='admin123',
            role='admin',
            name='管理员'
        )
        print(f"✓ 创建管理员账户成功：学号={admin.student_id}, 密码=admin123")
    else:
        print(f"✓ 管理员账户已存在：学号={admin.student_id}")

    # 创建测试学生账户
    student = User.get_by_student_id('87654321')
    if not student:
        student = User.create_user(
            student_id='87654321',
            password='student123',
            role='student',
            name='测试学生'
        )
        print(f"✓ 创建学生账户成功：学号={student.student_id}, 密码=student123")
    else:
        print(f"✓ 学生账户已存在：学号={student.student_id}")

    print("\n数据库初始化完成！")
    print("\n测试账户信息：")
    print("管理员：学号=12345678, 密码=admin123")
    print("学生：学号=87654321, 密码=student123")
