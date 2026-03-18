"""
测试用户管理功能
"""

from app import create_app, db
from config.settings import config
import os

app = create_app(config[os.environ.get('FLASK_ENV', 'default')])

with app.app_context():
    from app.models.user import User
    
    print("=" * 60)
    print("用户管理功能测试")
    print("=" * 60)
    
    # 1. 测试创建用户
    print("\n1. 测试创建用户...")
    try:
        test_user = User.create_user(
            student_id='20240001',
            password='test123',
            role='student',
            name='测试学生'
        )
        print(f"   ✓ 创建用户成功：{test_user.student_id}")
    except Exception as e:
        print(f"   ✗ 创建失败：{str(e)}")
    
    # 2. 测试更新用户
    print("\n2. 测试更新用户信息...")
    try:
        updated_user = User.update_user(
            test_user.id,
            name='更新后的名字',
            email='test@example.com'
        )
        print(f"   ✓ 更新用户成功：{updated_user.name}, {updated_user.email}")
    except Exception as e:
        print(f"   ✗ 更新失败：{str(e)}")
    
    # 3. 测试重置密码
    print("\n3. 测试重置密码...")
    try:
        result = User.reset_password('20240001', 'newpassword123')
        if result:
            print(f"   ✓ 重置密码成功")
            # 验证新密码
            user = User.get_by_student_id('20240001')
            if user.check_password('newpassword123'):
                print(f"   ✓ 密码验证通过")
        else:
            print(f"   ✗ 重置失败")
    except Exception as e:
        print(f"   ✗ 失败：{str(e)}")
    
    # 4. 测试删除用户
    print("\n4. 测试删除用户...")
    try:
        result = User.delete_user(test_user.id)
        if result:
            print(f"   ✓ 删除用户成功")
            # 验证是否真的删除了
            deleted_user = User.get_by_student_id('20240001')
            if not deleted_user:
                print(f"   ✓ 确认已删除")
            else:
                print(f"   ✗ 删除失败，用户仍存在")
        else:
            print(f"   ✗ 删除失败")
    except Exception as e:
        print(f"   ✗ 失败：{str(e)}")
    
    # 5. 测试批量操作（可选）
    print("\n5. 测试查询所有用户...")
    try:
        users = User.query.all()
        print(f"   ✓ 当前共有 {len(users)} 个用户")
        for user in users:
            status = "正常" if user.is_active else "禁用"
            print(f"      - {user.student_id} ({user.name}) - {user.role} - {status}")
    except Exception as e:
        print(f"   ✗ 查询失败：{str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
