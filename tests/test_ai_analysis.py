"""
AI 分析服务测试脚本
测试 AI 分析和报告生成功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config.settings import Config

def test_ai_analysis():
    """测试 AI 分析服务"""
    print("=" * 60)
    print("测试 AI 分析服务")
    print("=" * 60)
    
    # 创建应用
    app = create_app(Config)
    
    with app.app_context():
        try:
            from app.services.ai_analysis_service import AIAnalysisService
            
            service = AIAnalysisService()
            
            print("\n✅ AI 分析服务实例化成功!")
            
            # 检查方法
            assert hasattr(service, 'analyze_assessment'), "缺少 analyze_assessment 方法"
            assert hasattr(service, '_build_prompt'), "缺少 _build_prompt 方法"
            assert hasattr(service, '_parse_model_response'), "缺少 _parse_model_response 方法"
            assert hasattr(service, '_get_rule_based_result'), "缺少 _get_rule_based_result 方法"
            
            print("✅ AI 分析方法检查通过!")
            
            # 测试风险等级判断逻辑
            from app.services.assessment_service import AssessmentService
            
            # 测试不同分数对应的风险等级
            test_scores = [
                (20, '低风险'),  # ≤30
                (50, '中风险'),  # ≤55
                (70, '高风险'),  # ≤80
                (100, '极高风险')  # >80
            ]
            
            print("\n测试风险等级判断:")
            for score, expected_level in test_scores:
                level = AssessmentService.determine_risk_level(score)
                status = "✅" if level == expected_level else "❌"
                print(f"   {status} 分数：{score} -> {level} (期望：{expected_level})")
                assert level == expected_level, f"风险等级判断错误：{score}"
            
            print("✅ 风险等级判断测试通过!")
            
            # 测试 DashScope API 配置
            import dashscope
            api_key = app.config.get('DASHSCOPE_API_KEY')
            if api_key:
                print(f"\n✅ DashScope API Key 已配置：{api_key[:10]}...")
                dashscope.api_key = api_key
                print("✅ DashScope 初始化成功!")
            else:
                print("\n⚠️  DashScope API Key 未配置，AI 分析功能将不可用")
            
        except Exception as e:
            print(f"❌ AI 分析服务测试失败：{e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "=" * 60)
    print("✅ AI 分析服务测试全部通过!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_ai_analysis()
    sys.exit(0 if success else 1)
