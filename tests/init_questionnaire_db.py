"""
初始化问卷题目数据库
将原有的固定题目导入到数据库，支持动态管理
"""

import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models.questionnaire import QuestionnaireQuestion, QuestionnaireConfig
import json


def init_questionnaire_questions():
    """初始化问卷题目"""
    
    # 认知维度题目（1-10 题）
    cognitive_questions = [
        {
            'question_number': 1,
            'category': 'cognitive',
            'dimension': 'cognitive',
            'question_text': '你清楚电信网络诈骗的常见手段吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '完全不符合',
                '2': '不太符合',
                '3': '一般',
                '4': '比较符合',
                '5': '非常符合'
            }, ensure_ascii=False)
        },
        {
            'question_number': 2,
            'category': 'cognitive',
            'dimension': 'cognitive',
            'question_text': '你知道国家反诈中心 App 的主要功能吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '完全不知道',
                '2': '知道一点',
                '3': '了解部分功能',
                '4': '比较了解',
                '5': '非常清楚所有功能'
            }, ensure_ascii=False)
        },
        {
            'question_number': 3,
            'category': 'cognitive',
            'dimension': 'cognitive',
            'question_text': '你能准确识别"刷单返利""冒充公检法""杀猪盘"等诈骗类型吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '完全不能',
                '2': '能识别少数',
                '3': '能识别部分',
                '4': '大部分能识别',
                '5': '全部能准确识别'
            }, ensure_ascii=False)
        },
        {
            'question_number': 4,
            'category': 'cognitive',
            'dimension': 'cognitive',
            'question_text': '你了解受骗后的正确止损流程（保留证据→报警→冻结账户）吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '完全不了解',
                '2': '了解一点',
                '3': '大致了解',
                '4': '比较清楚',
                '5': '非常清楚完整流程'
            }, ensure_ascii=False)
        },
        {
            'question_number': 5,
            'category': 'cognitive',
            'dimension': 'cognitive',
            'question_text': '你知道"金钟罩"小程序的作用吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '完全不知道',
                '2': '听说过',
                '3': '知道基本作用',
                '4': '比较了解',
                '5': '非常清楚功能和使用方法'
            }, ensure_ascii=False)
        },
        {
            'question_number': 6,
            'category': 'cognitive',
            'dimension': 'cognitive',
            'question_text': '你经常阅读学校或官方发布的反诈宣传材料吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从不',
                '2': '很少',
                '3': '偶尔',
                '4': '经常',
                '5': '总是主动阅读'
            }, ensure_ascii=False)
        },
        {
            'question_number': 7,
            'category': 'cognitive',
            'dimension': 'cognitive',
            'question_text': '你认为自己对网络诈骗的识别能力如何？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '非常差',
                '2': '比较差',
                '3': '一般',
                '4': '比较好',
                '5': '非常好'
            }, ensure_ascii=False)
        },
        {
            'question_number': 8,
            'category': 'cognitive',
            'dimension': 'cognitive',
            'question_text': '你知道如何验证陌生来电/短信的真实性吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '完全不知道',
                '2': '知道很少方法',
                '3': '知道一些方法',
                '4': '掌握多种验证方法',
                '5': '熟练掌握所有验证方法'
            }, ensure_ascii=False)
        },
        {
            'question_number': 9,
            'category': 'cognitive',
            'dimension': 'cognitive',
            'question_text': '你了解个人信息泄露的常见途径吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '完全不了解',
                '2': '了解一点',
                '3': '大致了解',
                '4': '比较清楚',
                '5': '非常清楚各种途径'
            }, ensure_ascii=False)
        },
        {
            'question_number': 10,
            'category': 'cognitive',
            'dimension': 'cognitive',
            'question_text': '你知道受骗后正确报警和联系银行的流程吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '完全不知道',
                '2': '知道一点',
                '3': '大致了解',
                '4': '比较清楚',
                '5': '非常清楚完整流程'
            }, ensure_ascii=False)
        }
    ]
    
    # 行为风险维度题目（11-20 题）
    behavior_questions = [
        {
            'question_number': 11,
            'category': 'behavior',
            'dimension': 'behavior',
            'question_text': '你是否经常点击陌生链接或下载不明 App？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从不',
                '2': '很少',
                '3': '有时',
                '4': '经常',
                '5': '非常经常'
            }, ensure_ascii=False)
        },
        {
            'question_number': 12,
            'category': 'behavior',
            'dimension': 'behavior',
            'question_text': '你是否参与过"刷单返利""任务赚钱"等活动？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从未参与',
                '2': '很少参与',
                '3': '偶尔参与',
                '4': '经常参与',
                '5': '频繁参与'
            }, ensure_ascii=False)
        },
        {
            'question_number': 13,
            'category': 'behavior',
            'dimension': 'behavior',
            'question_text': '你是否轻易把验证码、银行卡信息告诉陌生人？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从不',
                '2': '很少',
                '3': '有时',
                '4': '经常',
                '5': '很容易'
            }, ensure_ascii=False)
        },
        {
            'question_number': 14,
            'category': 'behavior',
            'dimension': 'behavior',
            'question_text': '你是否在微信/QQ 上添加大量陌生好友？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从不',
                '2': '很少',
                '3': '有时',
                '4': '经常',
                '5': '非常频繁'
            }, ensure_ascii=False)
        },
        {
            'question_number': 15,
            'category': 'behavior',
            'dimension': 'behavior',
            'question_text': '你是否使用同一密码在多个平台注册？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从不',
                '2': '很少',
                '3': '有几个平台',
                '4': '很多平台',
                '5': '所有平台都用同一密码'
            }, ensure_ascii=False)
        },
        {
            'question_number': 16,
            'category': 'behavior',
            'dimension': 'behavior',
            'question_text': '你容易被"高回报、低风险"的广告吸引吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '完全不会',
                '2': '不太会',
                '3': '有时会',
                '4': '经常会',
                '5': '很容易被吸引'
            }, ensure_ascii=False)
        },
        {
            'question_number': 17,
            'category': 'behavior',
            'dimension': 'behavior',
            'question_text': '你是否在二手平台/校园贷平台频繁交易？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从不',
                '2': '很少',
                '3': '偶尔',
                '4': '经常',
                '5': '非常频繁'
            }, ensure_ascii=False)
        },
        {
            'question_number': 18,
            'category': 'behavior',
            'dimension': 'behavior',
            'question_text': '你遇到"限时优惠"或"最后机会"时会冲动消费/转账吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从不',
                '2': '很少',
                '3': '有时会',
                '4': '经常会',
                '5': '总是会'
            }, ensure_ascii=False)
        },
        {
            'question_number': 19,
            'category': 'behavior',
            'dimension': 'behavior',
            'question_text': '你下载 App 时会查看权限和开发者信息吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从不查看',
                '2': '很少查看',
                '3': '有时查看',
                '4': '经常查看',
                '5': '每次都仔细查看'
            }, ensure_ascii=False)
        },
        {
            'question_number': 20,
            'category': 'behavior',
            'dimension': 'behavior',
            'question_text': '你是否轻易相信"熟人/领导/客服"发来的紧急求助信息？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '完全不信',
                '2': '不太相信',
                '3': '半信半疑',
                '4': '比较容易相信',
                '5': '很容易相信'
            }, ensure_ascii=False)
        }
    ]
    
    # 经历与环境暴露维度题目（21-28 题）
    experience_questions = [
        {
            'question_number': 21,
            'category': 'experience',
            'dimension': 'experience',
            'question_text': '你或身边同学是否遭遇过电信诈骗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从未',
                '2': '很少',
                '3': '有过 1-2 次',
                '4': '多次',
                '5': '非常频繁'
            }, ensure_ascii=False)
        },
        {
            'question_number': 22,
            'category': 'experience',
            'dimension': 'experience',
            'question_text': '你每天使用微信/支付宝/抖音等 App 时长超过 4 小时吗？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从不超过',
                '2': '很少超过',
                '3': '有时超过',
                '4': '经常超过',
                '5': '每天都超过 4 小时'
            }, ensure_ascii=False)
        },
        {
            'question_number': 23,
            'category': 'experience',
            'dimension': 'experience',
            'question_text': '你是否经常收到陌生电话/短信/私信？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从不',
                '2': '很少',
                '3': '偶尔',
                '4': '经常',
                '5': '非常频繁'
            }, ensure_ascii=False)
        },
        {
            'question_number': 24,
            'category': 'experience',
            'dimension': 'experience',
            'question_text': '你是否在网络上公开过多个人信息（如手机号、身份证）？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从未',
                '2': '很少',
                '3': '有过几次',
                '4': '经常',
                '5': '频繁公开'
            }, ensure_ascii=False)
        },
        {
            'question_number': 25,
            'category': 'experience',
            'dimension': 'experience',
            'question_text': '你是否把银行卡绑定了多个高风险 App？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '没有',
                '2': '绑定 1-2 个',
                '3': '绑定 3-5 个',
                '4': '绑定多个',
                '5': '绑定了很多个'
            }, ensure_ascii=False)
        },
        {
            'question_number': 26,
            'category': 'experience',
            'dimension': 'experience',
            'question_text': '你是否参与过"网络贷款"或"校园贷"？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从未',
                '2': '考虑过但未参与',
                '3': '参与过 1 次',
                '4': '参与过多次',
                '5': '频繁参与'
            }, ensure_ascii=False)
        },
        {
            'question_number': 27,
            'category': 'experience',
            'dimension': 'experience',
            'question_text': '你是否在兼职群/投资群里活跃并转账？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从不',
                '2': '只看不说话',
                '3': '偶尔发言',
                '4': '经常发言并转账',
                '5': '非常活跃且频繁转账'
            }, ensure_ascii=False)
        },
        {
            'question_number': 28,
            'category': 'experience',
            'dimension': 'experience',
            'question_text': '你是否曾因网络兼职/投资被扣押资金或损失？',
            'min_score': 1,
            'max_score': 5,
            'weight': 1.0,
            'options_json': json.dumps({
                '1': '从未',
                '2': '差点被骗但成功避免',
                '3': '小额损失（500 元以下）',
                '4': '中等损失（500-5000 元）',
                '5': '重大损失（5000 元以上）'
            }, ensure_ascii=False)
        }
    ]
    
    # 开放题
    open_questions = [
        {
            'question_number': 29,
            'category': 'open',
            'dimension': None,
            'question_text': '请描述最近收到的一条可疑消息内容或聊天记录（可选）',
            'min_score': 0,
            'max_score': 0,
            'weight': 0,
            'options_json': None,
            'is_required': False
        },
        {
            'question_number': 30,
            'category': 'open',
            'dimension': None,
            'question_text': '请描述最近遇到的可疑链接、二维码或截图场景（可选）',
            'min_score': 0,
            'max_score': 0,
            'weight': 0,
            'options_json': None,
            'is_required': False
        }
    ]
    
    # 合并所有题目
    all_questions = cognitive_questions + behavior_questions + experience_questions + open_questions
    
    app = create_app()
    with app.app_context():
        # 检查是否已存在题目
        existing_count = QuestionnaireQuestion.query.count()
        if existing_count > 0:
            print(f"⚠️  数据库中已有{existing_count}道题目，跳过初始化")
            print("如需重新初始化，请先清空 questionnaire_questions 表")
            return
        
        # 批量插入题目
        for q_data in all_questions:
            question = QuestionnaireQuestion(**q_data)
            db.session.add(question)
        
        db.session.commit()
        
        # 设置全局配置
        QuestionnaireConfig.set_config(
            'url_risk_score_per_link',
            '10',
            '每个风险链接加分值'
        )
        QuestionnaireConfig.set_config(
            'max_url_risk_score',
            '20',
            'URL 风险加分上限'
        )
        QuestionnaireConfig.set_config(
            'enable_url_detection',
            'true',
            '是否启用 URL 检测'
        )
        
        print(f"✅ 成功初始化{len(all_questions)}道问卷题目")
        print(f"   - 认知维度：{len(cognitive_questions)}题")
        print(f"   - 行为维度：{len(behavior_questions)}题")
        print(f"   - 经历维度：{len(experience_questions)}题")
        print(f"   - 开放题：{len(open_questions)}题")
        print(f"\n📋 全局配置:")
        print(f"   - 风险链接加分：10 分/个")
        print(f"   - URL 风险加分上限：20 分")
        print(f"   - 启用 URL 检测：是")


if __name__ == '__main__':
    init_questionnaire_questions()
