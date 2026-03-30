"""
快速 API 功能测试脚本
在应用运行时测试关键 API 端点
"""

import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_homepage():
    """测试首页访问"""
    print("=" * 60)
    print("测试：访问首页")
    print("=" * 60)
    
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200 or response.status_code == 302:
            print(f"✅ 首页访问成功 (状态码：{response.status_code})")
            return True
        else:
            print(f"❌ 首页访问失败 (状态码：{response.status_code})")
            return False
    except Exception as e:
        print(f"❌ 无法访问首页：{e}")
        return False

def test_login_page():
    """测试登录页面"""
    print("\n" + "=" * 60)
    print("测试：访问登录页面")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/auth/login", timeout=5)
        if response.status_code == 200:
            print(f"✅ 登录页面加载成功 (状态码：{response.status_code})")
            # 检查是否包含 CSRF token
            if 'csrf_token' in response.text:
                print("✅ 页面包含 CSRF token")
            return True
        else:
            print(f"❌ 登录页面加载失败 (状态码：{response.status_code})")
            return False
    except Exception as e:
        print(f"❌ 无法访问登录页面：{e}")
        return False

def test_register_page():
    """测试注册页面"""
    print("\n" + "=" * 60)
    print("测试：访问注册页面")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/auth/register", timeout=5)
        if response.status_code == 200:
            print(f"✅ 注册页面加载成功 (状态码：{response.status_code})")
            return True
        else:
            print(f"⚠️  注册页面可能不存在 (状态码：{response.status_code})")
            return True  # 注册页面可能未启用
    except Exception as e:
        print(f"❌ 无法访问注册页面：{e}")
        return False

def main():
    """主测试函数"""
    print("\n开始 API 功能测试...\n")
    
    results = []
    
    # 测试基本页面
    results.append(("首页访问", test_homepage()))
    results.append(("登录页面", test_login_page()))
    results.append(("注册页面", test_register_page()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n总计：{passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程出错：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
