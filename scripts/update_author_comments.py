"""
批量更新 Python 文件的 Author 注释脚本
将所有文件中的"小土豆 233"替换为"脆心柚"
"""

import os
import re

def update_author_in_file(file_path):
    """更新单个文件的 Author 信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换 Author 信息
        new_content = re.sub(
            r'# Author: 脆心柚',
            '# Author: 脆心柚',
            content
        )
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 已更新：{file_path}")
            return True
        else:
            print(f"⚠️  无需更新：{file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("批量更新 Author 信息")
    print("=" * 60)
    
    # 项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 需要更新的目录
    target_dirs = [
        os.path.join(root_dir, 'app'),
        os.path.join(root_dir, 'config'),
        os.path.join(root_dir, 'scripts'),
    ]
    
    updated_count = 0
    total_count = 0
    
    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            continue
            
        print(f"\n扫描目录：{target_dir}")
        
        # 遍历所有 Python 文件
        for root, dirs, files in os.walk(target_dir):
            # 跳过 __pycache__ 等目录
            dirs[:] = [d for d in dirs if not d.startswith('__')]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    total_count += 1
                    
                    if update_author_in_file(file_path):
                        updated_count += 1
    
    print("\n" + "=" * 60)
    print(f"处理完成!")
    print(f"总文件数：{total_count}")
    print(f"已更新：{updated_count}")
    print(f"未变更：{total_count - updated_count}")
    print("=" * 60)

if __name__ == '__main__':
    main()
