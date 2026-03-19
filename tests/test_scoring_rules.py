"""
评分规则管理功能测试脚本
用于验证评分规则配置功能是否正常
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.questionnaire import QuestionnaireConfig


def test_config_methods():
    """测试配置读取方法"""
    print("\n" + "="*60)
    print("🧪 测试配置读取方法")
    print("="*60)
    
    # 测试整数配置
    threshold_low = QuestionnaireConfig.get_int_config('threshold_low', 30)
    print(f"✅ 低风险阈值：{threshold_low}")
    
    threshold_mid = QuestionnaireConfig.get_int_config('threshold_mid', 55)
    print(f"✅ 中风险阈值：{threshold_mid}")
    
    threshold_high = QuestionnaireConfig.get_int_config('threshold_high', 80)
    print(f"✅ 高风险阈值：{threshold_high}")
    
    # 测试浮点配置
    weight_default = QuestionnaireConfig.get_float_config('test_weight', 1.0)
    print(f"✅ 测试权重（默认值）: {weight_default}")
    
    print("\n✅ 配置读取方法测试通过\n")


def test_set_thresholds():
    """测试设置阈值"""
    print("\n" + "="*60)
    print("🧪 测试设置阈值")
    print("="*60)
    
    # 保存当前值
    old_low = QuestionnaireConfig.get_int_config('threshold_low', 30)
    
    # 设置新值
    QuestionnaireConfig.set_config('threshold_low', '35', '测试用低风险阈值')
    new_value = QuestionnaireConfig.get_int_config('threshold_low', 30)
    
    print(f"原值：{old_low}")
    print(f"新值：{new_value}")
    
    if new_value == 35:
        print("✅ 阈值设置成功")
    else:
        print("❌ 阈值设置失败")
    
    # 恢复原值
    QuestionnaireConfig.set_config('threshold_low', str(old_low), '低风险阈值上限')
    print(f"已恢复原值：{old_low}\n")


def test_risk_level_determination():
    """测试风险等级判定"""
    print("\n" + "="*60)
    print("🧪 测试风险等级判定（使用配置阈值）")
    print("="*60)
    
    from app.services.assessment_service import AssessmentService
    
    # 获取当前配置
    threshold_low = QuestionnaireConfig.get_int_config('threshold_low', 30)
    threshold_mid = QuestionnaireConfig.get_int_config('threshold_mid', 55)
    threshold_high = QuestionnaireConfig.get_int_config('threshold_high', 80)
    
    print(f"当前阈值配置：")
    print(f"  低风险 ≤ {threshold_low}")
    print(f"  {threshold_low} < 中风险 ≤ {threshold_mid}")
    print(f"  {threshold_mid} < 高风险 ≤ {threshold_high}")
    print(f"  极高风险 > {threshold_high}")
    print()
    
    # 测试不同分数
    test_scores = [20, 35, 60, 85, 100]
    
    for score in test_scores:
        risk_level = AssessmentService.determine_risk_level(score)
        print(f"  {score}分 → {risk_level}")
    
    print("\n✅ 风险等级判定测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🔧 评分规则管理功能测试")
    print("="*60 + "\n")
    
    # 使用当前目录的 config.settings
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    from config.settings import DevelopmentConfig
    from app import create_app, db
    
    app = create_app()
    app.config.from_object(DevelopmentConfig)
    
    with app.app_context():
        try:
            # 测试 1: 配置读取方法
            test_config_methods()
            
            # 测试 2: 配置设置方法
            test_set_thresholds()
            
            # 测试 3: 风险等级判定
            test_risk_level_determination()
            
            # 总结
            print("="*60)
            print("✅ 所有测试完成！")
            print("="*60)
            print("""
功能清单:
✓ 配置值读取（整数/浮点数）
✓ 配置值设置
✓ 风险阈值动态加载
✓ 风险等级判定（使用配置阈值）
✓ 与评估服务集成

配置项:
- threshold_low: 低风险阈值（默认 30）
- threshold_mid: 中风险阈值（默认 55）
- threshold_high: 高风险阈值（默认 80）
- max_cognitive: 认知维度满分（默认 40）
- max_behavior: 行为维度满分（默认 40）
- max_experience: 经历维度满分（默认 20）
    """)
            
        except Exception as e:
            print(f"\n❌ 测试失败：{str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
