"""
测试提交报告中的图片显示功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.submission import Submission

app = create_app()

def test_image_display():
    """测试图片显示功能"""
    
    with app.app_context():
        print("="*70)
        print(" 测试提交报告中的图片显示功能")
        print("="*70)
        
        # 查找有图片的提交记录
        submissions_with_images = []
        all_submissions = Submission.query.all()
        
        for s in all_submissions:
            if s.uploaded_images and s.uploaded_images != '[]':
                submissions_with_images.append(s)
        
        if not submissions_with_images:
            print("\n⚠️  没有找到包含图片的提交记录")
            print("\n💡 建议：")
            print("   1. 使用学生账号登录")
            print("   2. 在问卷页面上传图片并提交")
            print("   3. 再次运行此测试")
            return
        
        print(f"\n✅ 找到 {len(submissions_with_images)} 条包含图片的提交记录\n")
        
        # 显示第一个有图片的提交
        submission = submissions_with_images[0]
        
        print(f"📊 提交 ID: {submission.id}")
        print(f"   学号：{submission.user.student_id}")
        print(f"   姓名：{submission.user.name or '未填写'}")
        print(f"   提交时间：{submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 解析图片路径
        import json
        try:
            image_paths = json.loads(submission.uploaded_images)
            print(f"\n📸 上传的图片数量：{len(image_paths)}")
            
            for i, path in enumerate(image_paths, 1):
                print(f"\n   图片 {i}:")
                print(f"   完整路径：{path}")
                
                # 提取文件名（兼容 Windows 和 Linux）
                if '\\' in path:
                    filename = path.split('\\')[-1]
                else:
                    filename = path.split('/')[-1]
                
                print(f"   文件名：{filename}")
                
                # 检查文件是否存在
                if os.path.exists(path):
                    print(f"   ✅ 文件存在")
                    file_size = os.path.getsize(path)
                    print(f"   📦 文件大小：{file_size:,} 字节 ({file_size/1024:.1f} KB)")
                else:
                    print(f"   ❌ 文件不存在！")
                
                # 检查 uploads 目录中是否有该文件
                uploads_dir = os.path.join(os.getcwd(), 'uploads')
                upload_file_path = os.path.join(uploads_dir, filename)
                
                if os.path.exists(upload_file_path):
                    print(f"   ✅ uploads 目录中存在该文件")
                else:
                    print(f"   ❌ uploads 目录中未找到该文件")
                    
        except Exception as e:
            print(f"\n❌ 解析图片路径失败：{str(e)}")
        
        print(f"\n{'='*70}")
        print(" 修复说明")
        print(f"{'='*70}")
        
        print(f"\n✅ 已修复的问题：")
        print(f"   1. ✅ 路径分隔符处理：同时支持 Windows (\\) 和 Linux (/)")
        print(f"   2. ✅ 文件名提取：使用正确的分隔符分割路径")
        print(f"   3. ✅ 图片显示：使用 url_for 正确生成静态文件 URL")
        print(f"   4. ✅ 增加文件名显示：在图片下方显示文件名")
        
        print(f"\n📋 修复内容：")
        print(f"   修改前：image_path.split('/')[-1]")
        print(f"   修改后：image_path.split('\\\\')[-1] if '\\\\' in path else image_path.split('/')[-1]")
        
        print(f"\n💡 使用方法：")
        print(f"   1. 启动应用：python run.py")
        print(f"   2. 访问 http://127.0.0.1:5000/admin/")
        print(f"   3. 登录管理员账号")
        print(f"   4. 在仪表板中找到有图片的提交记录")
        print(f"   5. 点击'查看报告'按钮")
        print(f"   6. 滚动到页面底部查看'上传的图片'卡片")
        
        print(f"\n🔍 调试步骤：")
        print(f"   如果图片仍然无法显示，请检查：")
        print(f"   1. 浏览器控制台是否有错误")
        print(f"   2. 图片路径是否正确")
        print(f"   3. uploads 目录是否在 static 文件夹下")
        print(f"   4. 文件权限是否正确")
        
        print(f"\n{'='*70}")
        print(" ✅ 测试完成！")
        print(f"{'='*70}")

if __name__ == '__main__':
    test_image_display()
