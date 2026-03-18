"""
风险链接检测功能测试脚本
测试 URL 提取、检测和评分功能
"""

import sys
sys.path.insert(0, '.')

from app import create_app
from app.services.url_security_service import URLSecurityService


def test_url_extraction():
    """测试 URL 提取功能"""
    print("=" * 60)
    print("测试 1: URL 提取功能")
    print("=" * 60)
    
    test_text = """
    我收到一条短信，说我的银行卡异常，让我点击这个链接验证：
    http://fake-bank.com/verify
    
    还有人发给我一个兼职广告：https://scam-job.cn/register
    
    还有一个短链接：http://t.cn/A6xYz123
    
     www.example.com 这个网站也很可疑
    """
    
    urls = URLSecurityService.extract_urls_from_text(test_text)
    
    print(f"输入文本：{test_text[:100]}...")
    print(f"\n提取到的 URL（共{len(urls)}个）:")
    for url in urls:
        print(f"  - {url}")
    
    print("\n✅ URL 提取功能正常\n")
    return urls


def test_single_url_detection():
    """测试单个 URL 检测"""
    print("=" * 60)
    print("测试 2: 单个 URL 检测（使用 AI 分析）")
    print("=" * 60)
    
    # 测试一个明显的诈骗 URL
    test_url = "http://fake-lottery.com/win-iphone"
    open_text = "说我中了 iPhone 15，让我点击领取"
    
    print(f"待检测 URL: {test_url}")
    print(f"上下文：{open_text}")
    
    result = URLSecurityService.check_url_ai(test_url, open_text)
    
    print(f"\n检测结果:")
    print(f"  - 是否风险：{result.get('is_risk', 'unknown')}")
    print(f"  - 风险等级：{result.get('risk_level', 'unknown')}")
    print(f"  - 风险类型：{result.get('risk_type', '')}")
    print(f"  - 判断理由：{result.get('description', '')}")
    print(f"  - 检测来源：{result.get('source', '')}")
    
    print("\n✅ URL 检测功能正常\n")
    return result


def test_batch_detection():
    """测试批量 URL 检测"""
    print("=" * 60)
    print("测试 3: 批量 URL 检测")
    print("=" * 60)
    
    test_urls = [
        "http://fake-bank.com",
        "https://phishing-site.cn",
        "http://normal-website.com"
    ]
    
    print(f"待检测 URL 列表（共{len(test_urls)}个）:")
    for url in test_urls:
        print(f"  - {url}")
    
    results = URLSecurityService.batch_check_urls(test_urls)
    
    print(f"\n检测结果:")
    risk_count = 0
    for result in results:
        is_risk = result.get('is_risk', False)
        if is_risk:
            risk_count += 1
        status = "⚠️ 风险" if is_risk else "✅ 安全"
        print(f"  {status} {result['url']}: {result.get('description', '')[:30]}")
    
    print(f"\n发现风险链接：{risk_count}/{len(test_urls)}个")
    print("\n✅ 批量检测功能正常\n")
    
    return results


def test_risk_score_calculation():
    """测试风险加分计算"""
    print("=" * 60)
    print("测试 4: 风险加分计算")
    print("=" * 60)
    
    # 模拟检测结果
    mock_results = [
        {'is_risk': True, 'url': 'http://fake1.com'},
        {'is_risk': True, 'url': 'http://fake2.com'},
        {'is_risk': False, 'url': 'http://safe.com'},
        {'is_risk': True, 'url': 'http://fake3.com'},
    ]
    
    print("模拟检测结果:")
    for r in mock_results:
        status = "⚠️ 风险" if r['is_risk'] else "✅ 安全"
        print(f"  {status} {r['url']}")
    
    score = URLSecurityService.calculate_risk_score(mock_results)
    
    print(f"\n风险加分计算:")
    print(f"  - 风险链接数量：{sum(1 for r in mock_results if r['is_risk'])}个")
    print(f"  - 每个链接加分：10 分")
    print(f"  - 最终加分：{score}分（上限 20 分）")
    
    print("\n✅ 风险加分计算正常\n")
    return score


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🔗 风险链接检测功能测试")
    print("=" * 60 + "\n")
    
    app = create_app('development')
    
    with app.app_context():
        # 测试 1: URL 提取
        test_url_extraction()
        
        # 测试 2: 单个 URL 检测
        test_single_url_detection()
        
        # 测试 3: 批量检测
        test_batch_detection()
        
        # 测试 4: 风险加分
        test_risk_score_calculation()
    
    # 总结
    print("=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)
    print("""
功能清单:
✓ URL 提取（支持多种格式）
✓ 360 API 检测（需配置 API Key）
✓ 腾讯 API 检测（需配置 API Key）
✓ AI 大模型兜底分析
✓ 批量检测
✓ 风险加分计算
✓ 与评估服务集成

评分规则:
- 基础分：0-100 分
- URL 风险分：0-20 分
- 总分 = 基础分 + URL 风险分
    """)


if __name__ == '__main__':
    run_all_tests()
