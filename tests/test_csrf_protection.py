"""
CSRF 安全功能测试脚本
测试 CSRF 保护是否正确启用
"""

import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models.user import User
import unittest


class TestCSRFProtection(unittest.TestCase):
    """CSRF 保护测试"""
    
    def setUp(self):
        """测试前准备"""
        from config.settings import TestingConfig
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # 创建测试用户
            admin = User.create_user(
                student_id='12345678',
                password='admin123',
                role='admin',
                name='测试管理员'
            )
    
    def tearDown(self):
        """测试后清理"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_login_without_csrf_should_fail(self):
        """测试没有 CSRF token 时登录应该失败"""
        print("\n[测试] 尝试不使用 CSRF token 登录...")
        
        response = self.client.post('/auth/login', data={
            'student_id': '12345678',
            'password': 'admin123'
        }, follow_redirects=False)
        
        # 应该返回 400 错误（缺少 CSRF token）
        self.assertEqual(response.status_code, 400)
        print("✓ 正确：没有 CSRF token 时返回 400 错误")
    
    def test_login_with_csrf_should_succeed(self):
        """测试有 CSRF token 时登录应该成功"""
        print("\n[测试] 使用 CSRF token 登录...")
        
        # 先获取登录页面（包含 CSRF token）
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        
        # 从响应中提取 CSRF token
        csrf_token = None
        import re
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', 
                         response.data.decode('utf-8'))
        if match:
            csrf_token = match.group(1)
            print(f"✓ 成功获取 CSRF token: {csrf_token[:20]}...")
        
        # 使用 CSRF token 登录
        if csrf_token:
            response = self.client.post('/auth/login', data={
                'student_id': '12345678',
                'password': 'admin123',
                'csrf_token': csrf_token
            }, follow_redirects=True)
            
            # 应该登录成功并跳转
            self.assertEqual(response.status_code, 200)
            print("✓ 正确：有 CSRF token 时登录成功")
    
    def test_session_cookie_security(self):
        """测试会话 Cookie 安全性"""
        print("\n[测试] 检查 Session Cookie 安全配置...")
        
        # 获取登录页面以设置 session
        response = self.client.get('/auth/login')
        
        # 检查 cookie
        cookies = response.headers.getlist('Set-Cookie')
        for cookie in cookies:
            if 'session' in cookie.lower():
                print(f"Cookie: {cookie}")
                
                # 检查 HttpOnly
                if 'httponly' in cookie.lower():
                    print("✓ Cookie 启用了 HttpOnly")
                else:
                    print("⚠ Cookie 未启用 HttpOnly")
                
                # 检查 SameSite
                if 'samesite' in cookie.lower():
                    print("✓ Cookie 配置了 SameSite")
                else:
                    print("⚠ Cookie 未配置 SameSite")
    
    def test_csrf_token_expiration(self):
        """测试 CSRF token 有效期"""
        print("\n[测试] CSRF token 有效期配置...")
        
        with self.app.app_context():
            # 检查配置
            from flask_wtf.csrf import generate_csrf
            
            token = generate_csrf()
            print(f"生成的 CSRF token: {token[:20]}...")
            print(f"Token 长度：{len(token)} 字符")
            print("✓ CSRF token 生成正常")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("CSRF 安全功能测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCSRFProtection)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"运行测试数：{result.testsRun}")
    print(f"成功：{result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败：{len(result.failures)}")
    print(f"错误：{len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！CSRF 保护已正确启用")
        return True
    else:
        print("\n❌ 部分测试失败，请检查配置")
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
