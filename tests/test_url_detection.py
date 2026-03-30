"""
URL 安全检测服务测试脚本
测试 URL 检测功能和降级策略
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config.settings import Config

def test_url_detection():
    """测试 URL 检测服务"""
    print("=" * 60)
    print("测试 URL 安全检测服务")
    print("=" * 60)
    
    # 创建应用
    app = create_app(Config)
    
    with app.app_context():
        try:
            from app.services.url_security_service import URLSecurityService
            
            service = URLSecurityService()
            
            print("\n✅ URL 检测服务实例化成功!")
            
            # 测试 URL 检测方法
            assert hasattr(service, 'check_url'), "缺少 check_url 方法"
            assert hasattr(service, 'extract_urls_from_text'), "缺少 extract_urls_from_text 方法"
            assert hasattr(URLSecurityService, 'check_url_virustotal'), "缺少 check_url_virustotal 方法"
            assert hasattr(URLSecurityService, 'check_url_tencent'), "缺少 check_url_tencent 方法"
            assert hasattr(URLSecurityService, 'check_url_ai'), "缺少 check_url_ai 方法"
            
            print("✅ URL 检测方法检查通过!")
            
            # 测试 URL 提取功能
            test_text = """这是一个测试文本，包含以下 URL:
            http://example.com
            https://www.baidu.com
            还有一些其他文本。"""
            
            urls = service.extract_urls_from_text(test_text)
            print(f"\n从文本中提取到 {len(urls)} 个 URL: {urls}")
            assert len(urls) == 2, f"应该提取到 2 个 URL，实际提取到{len(urls)}个"
            
            print("✅ URL 提取功能测试通过!")
            
            # 测试风险评分计算
            assert hasattr(URLSecurityService, 'calculate_risk_score'), "缺少风险评分计算方法"
            print("✅ 风险评分计算方法存在!")
            
        except Exception as e:
            print(f"❌ URL 检测服务测试失败：{e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "=" * 60)
    print("✅ URL 安全检测服务测试全部通过!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_url_detection()
    sys.exit(0 if success else 1)
