"""
邮件服务测试脚本
测试邮件配置和初始化功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config.settings import Config

def test_email_config():
    """测试邮件配置"""
    print("=" * 60)
    print("测试邮件服务配置")
    print("=" * 60)
    
    # 创建应用
    app = create_app(Config)
    
    with app.app_context():
        # 检查配置
        print("\n✅ 邮件配置检查:")
        print(f"   MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"   MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"   MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
        print(f"   MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"   MAIL_USERNAME: {app.config.get('MAIL_USERNAME', '未配置')}")
        print(f"   MAIL_PASSWORD: {'*' * 10 if app.config.get('MAIL_PASSWORD') else '未配置'}")
        
        # 验证配置是否正确
        assert app.config.get('MAIL_SERVER') == 'smtp.qq.com', "邮件服务器配置错误"
        assert app.config.get('MAIL_PORT') == 465, "邮件端口配置错误"
        assert app.config.get('MAIL_USE_SSL') is True, "SSL 配置错误"
        assert app.config.get('MAIL_USE_TLS') is False, "TLS 应该禁用"
        
        print("\n✅ 邮件配置验证通过!")
        
        # 测试 Flask-Mail 初始化
        try:
            from flask_mail import Mail
            mail = Mail()
            mail.init_app(app)
            print("✅ Flask-Mail 初始化成功!")
        except Exception as e:
            print(f"❌ Flask-Mail 初始化失败：{e}")
            return False
        
        # 测试 EmailService
        try:
            from app.services.email_service import EmailService
            
            # 检查邮件发送方法是否存在
            assert hasattr(EmailService, 'send_email'), "缺少 send_email 方法"
            assert hasattr(EmailService, 'send_welcome_email'), "缺少 send_welcome_email 方法"
            assert hasattr(EmailService, 'send_risk_warning_email'), "缺少 send_risk_warning_email 方法"
            
            print("✅ EmailService 类方法检查通过!")
        except Exception as e:
            print(f"❌ EmailService 检查失败：{e}")
            return False
    
    print("\n" + "=" * 60)
    print("✅ 邮件服务配置测试全部通过!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_email_config()
    sys.exit(0 if success else 1)
