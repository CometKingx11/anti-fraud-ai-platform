"""
批量导入用户功能
支持从 CSV 文件批量导入用户
"""

import csv
from app import create_app, db
from config.settings import config
import os
from app.models.user import User
from app.utils.helpers import validate_student_id


def import_users_from_csv(file_path):
    """
    从 CSV 文件批量导入用户
    
    Args:
        file_path: CSV 文件路径
        
    Returns:
        dict: 导入结果统计
    """
    result = {
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    student_id = row.get('student_id', '').strip()
                    name = row.get('name', '').strip()
                    email = row.get('email', '').strip()
                    role = row.get('role', 'student').strip()
                    password = row.get('password', '123456').strip()
                    
                    # 验证学号
                    if not validate_student_id(student_id):
                        result['failed'] += 1
                        result['errors'].append(f"学号格式错误：{student_id}")
                        continue
                    
                    # 检查是否已存在
                    existing = User.get_by_student_id(student_id)
                    if existing:
                        result['failed'] += 1
                        result['errors'].append(f"学号已存在：{student_id}")
                        continue
                    
                    # 创建用户
                    User.create_user(
                        student_id=student_id,
                        password=password,
                        role=role,
                        name=name
                    )
                    result['success'] += 1
                    
                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append(f"导入失败 {student_id}: {str(e)}")
        
        return result
        
    except Exception as e:
        result['errors'].append(f"读取文件失败：{str(e)}")
        return result


if __name__ == '__main__':
    app = create_app(config[os.environ.get('FLASK_ENV', 'default')])
    
    with app.app_context():
        print("=" * 60)
        print("批量导入用户测试")
        print("=" * 60)
        
        # 示例 CSV 文件路径
        csv_file = 'users_import.csv'
        
        if os.path.exists(csv_file):
            print(f"\n正在从 {csv_file} 导入用户...")
            result = import_users_from_csv(csv_file)
            
            print(f"\n导入完成！")
            print(f"成功：{result['success']} 人")
            print(f"失败：{result['failed']} 人")
            
            if result['errors']:
                print("\n错误详情:")
                for error in result['errors']:
                    print(f"  - {error}")
        else:
            print(f"\n未找到导入文件：{csv_file}")
            print("\n请创建 CSV 文件，格式如下:")
            print("student_id,name,email,role,password")
            print("20240001，张三，zhangsan@example.com,student,123456")
            print("20240002，李四，lisi@example.com,student,123456")
        
        print("\n" + "=" * 60)
