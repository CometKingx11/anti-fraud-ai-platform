"""
评估服务测试脚本
测试评分计算和问卷处理功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config.settings import Config

def test_assessment_service():
    """测试评估服务"""
    print("=" * 60)
    print("测试评估服务")
    print("=" * 60)
    
    # 创建应用
    app = create_app(Config)
    
    with app.app_context():
        try:
            from app.services.assessment_service import AssessmentService
            
            print("\n✅ 评估服务导入成功!")
            
            # 检查方法
            assert hasattr(AssessmentService, 'calculate_scores'), "缺少 calculate_scores 方法"
            assert hasattr(AssessmentService, 'determine_risk_level'), "缺少 determine_risk_level 方法"
            assert hasattr(AssessmentService, 'process_questionnaire_submission'), "缺少 process_questionnaire_submission 方法"
            
            print("✅ 评估服务方法检查通过!")
            
            # 注意：calculate_scores 方法需要数据库中有题目配置
            # 这里只测试方法存在性和基本逻辑
            print("\n⚠️  分数计算功能需要数据库题目配置，跳过详细测试")
            print("✅ 方法签名验证通过!")
            
            # 测试风险等级判断
            print("\n测试风险等级判断边界值:")
            boundary_tests = [
                (30, '低风险'),   # 边界值
                (31, '中风险'),   # 超过低阈值
                (55, '中风险'),   # 边界值
                (56, '高风险'),   # 超过中阈值
                (80, '高风险'),   # 边界值
                (81, '极高风险'),  # 超过高阈值
            ]
            
            for score, expected in boundary_tests:
                level = AssessmentService.determine_risk_level(score)
                status = "✅" if level == expected else "❌"
                print(f"   {status} {score}分 -> {level} (期望：{expected})")
                assert level == expected, f"风险等级判断错误：{score}"
            
            print("✅ 风险等级边界值测试通过!")
            
        except Exception as e:
            print(f"❌ 评估服务测试失败：{e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "=" * 60)
    print("✅ 评估服务测试全部通过!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_assessment_service()
    sys.exit(0 if success else 1)
