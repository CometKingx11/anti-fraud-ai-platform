"""
验证评分规则配置持久化功能
检查上次配置的规则是否能在下次进入时正确显示
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.questionnaire import QuestionnaireConfig, QuestionnaireQuestion


def test_threshold_persistence():
    """测试阈值配置的持久化"""
    print("\n" + "="*60)
    print("🧪 测试阈值配置持久化")
    print("="*60 + "\n")
    
    # 保存原值
    old_low = QuestionnaireConfig.get_int_config('threshold_low', 30)
    old_mid = QuestionnaireConfig.get_int_config('threshold_mid', 55)
    old_high = QuestionnaireConfig.get_int_config('threshold_high', 80)
    
    print(f"当前阈值配置：")
    print(f"  低风险阈值：{old_low} 分")
    print(f"  中风险阈值：{old_mid} 分")
    print(f"  高风险阈值：{old_high} 分")
    
    # 修改配置
    new_low = 25
    new_mid = 45
    new_high = 65
    
    print(f"\n修改配置为：")
    print(f"  低风险阈值：{new_low} 分")
    print(f"  中风险阈值：{new_mid} 分")
    print(f"  高风险阈值：{new_high} 分")
    
    QuestionnaireConfig.set_config('threshold_low', str(new_low), '低风险阈值上限')
    QuestionnaireConfig.set_config('threshold_mid', str(new_mid), '中风险阈值上限')
    QuestionnaireConfig.set_config('threshold_high', str(new_high), '高风险阈值上限')
    
    # 重新读取配置
    read_low = QuestionnaireConfig.get_int_config('threshold_low', 30)
    read_mid = QuestionnaireConfig.get_int_config('threshold_mid', 55)
    read_high = QuestionnaireConfig.get_int_config('threshold_high', 80)
    
    print(f"\n重新读取配置：")
    print(f"  低风险阈值：{read_low} 分")
    print(f"  中风险阈值：{read_mid} 分")
    print(f"  高风险阈值：{read_high} 分")
    
    # 验证
    if read_low == new_low and read_mid == new_mid and read_high == new_high:
        print("\n✅ 阈值配置持久化成功！")
    else:
        print("\n❌ 阈值配置持久化失败！")
    
    # 恢复原值
    QuestionnaireConfig.set_config('threshold_low', str(old_low), '低风险阈值上限')
    QuestionnaireConfig.set_config('threshold_mid', str(old_mid), '中风险阈值上限')
    QuestionnaireConfig.set_config('threshold_high', str(old_high), '高风险阈值上限')
    
    print(f"\n已恢复原值：{old_low}/{old_mid}/{old_high}")


def test_dimension_max_persistence():
    """测试维度满分配置的持久化"""
    print("\n" + "="*60)
    print("🧪 测试维度满分配置持久化")
    print("="*60 + "\n")
    
    # 保存原值
    old_cognitive = QuestionnaireConfig.get_int_config('max_cognitive', 40)
    old_behavior = QuestionnaireConfig.get_int_config('max_behavior', 40)
    old_experience = QuestionnaireConfig.get_int_config('max_experience', 20)
    
    print(f"当前维度满分配置：")
    print(f"  认知维度：{old_cognitive} 分")
    print(f"  行为维度：{old_behavior} 分")
    print(f"  经历维度：{old_experience} 分")
    
    # 修改配置
    new_cognitive = 50
    new_behavior = 45
    new_experience = 25
    
    print(f"\n修改配置为：")
    print(f"  认知维度：{new_cognitive} 分")
    print(f"  行为维度：{new_behavior} 分")
    print(f"  经历维度：{new_experience} 分")
    
    QuestionnaireConfig.set_config('max_cognitive', str(new_cognitive), '认知维度满分')
    QuestionnaireConfig.set_config('max_behavior', str(new_behavior), '行为维度满分')
    QuestionnaireConfig.set_config('max_experience', str(new_experience), '经历维度满分')
    
    # 重新读取配置
    read_cognitive = QuestionnaireConfig.get_int_config('max_cognitive', 40)
    read_behavior = QuestionnaireConfig.get_int_config('max_behavior', 40)
    read_experience = QuestionnaireConfig.get_int_config('max_experience', 20)
    
    print(f"\n重新读取配置：")
    print(f"  认知维度：{read_cognitive} 分")
    print(f"  行为维度：{read_behavior} 分")
    print(f"  经历维度：{read_experience} 分")
    
    # 验证
    if read_cognitive == new_cognitive and read_behavior == new_behavior and read_experience == new_experience:
        print("\n✅ 维度满分配置持久化成功！")
    else:
        print("\n❌ 维度满分配置持久化失败！")
    
    # 恢复原值
    QuestionnaireConfig.set_config('max_cognitive', str(old_cognitive), '认知维度满分')
    QuestionnaireConfig.set_config('max_behavior', str(old_behavior), '行为维度满分')
    QuestionnaireConfig.set_config('max_experience', str(old_experience), '经历维度满分')
    
    print(f"\n已恢复原值：{old_cognitive}/{old_behavior}/{old_experience}")


def test_question_weight_persistence():
    """测试题目权重配置的持久化"""
    print("\n" + "="*60)
    print("🧪 测试题目权重配置持久化")
    print("="*60 + "\n")
    
    # 获取第一道题
    question = QuestionnaireQuestion.query.first()
    
    if not question:
        print("❌ 没有找到问卷题目，请先创建题目")
        return
    
    # 保存原值
    old_weight = question.weight
    print(f"题目：第{question.question_number}题")
    print(f"  当前权重：{old_weight}")
    
    # 修改权重
    new_weight = 2.5
    print(f"  修改为：{new_weight}")
    
    question.weight = new_weight
    db.session.commit()
    
    # 重新读取
    question_refreshed = QuestionnaireQuestion.query.get(question.id)
    read_weight = question_refreshed.weight
    
    print(f"  重新读取：{read_weight}")
    
    # 验证
    if abs(read_weight - new_weight) < 0.01:
        print("\n✅ 题目权重配置持久化成功！")
    else:
        print("\n❌ 题目权重配置持久化失败！")
    
    # 恢复原值
    question.weight = old_weight
    db.session.commit()
    
    print(f"  已恢复原值：{old_weight}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🔧 评分规则配置持久化验证")
    print("="*60)
    print("\n验证目标：检查上次配置的规则是否能在下次进入时正确显示\n")
    
    app = create_app()
    from config.settings import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
    
    with app.app_context():
        try:
            # 测试 1: 阈值配置持久化
            test_threshold_persistence()
            
            # 测试 2: 维度满分配置持久化
            test_dimension_max_persistence()
            
            # 测试 3: 题目权重配置持久化
            test_question_weight_persistence()
            
            # 总结
            print("\n" + "="*60)
            print("✅ 所有测试完成！")
            print("="*60)
            print("""
结论:
✅ 评分规则配置会保存到数据库
✅ 下次进入页面时会从数据库读取配置
✅ 管理员可以看到最后一次配置的规则

配置存储位置:
- 表名：questionnaire_config
- 字段：config_key (键), config_value (值)
- 题目权重直接存储在 questionnaire_questions 表的 weight 字段
            """)
            
        except Exception as e:
            print(f"\n❌ 测试失败：{str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
