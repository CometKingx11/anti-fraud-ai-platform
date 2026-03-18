"""手动添加问卷题目到数据库"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models.questionnaire import QuestionnaireQuestion
import json

app = create_app()

with app.app_context():
    # 检查是否已有题目
    count = QuestionnaireQuestion.query.count()
    if count > 0:
        print(f"数据库中已有 {count} 道题目")
        print("正在清空数据库...")
        QuestionnaireQuestion.query.delete()
        db.session.commit()
        print("✓ 数据库已清空")
    
    # 认知维度题目（1-10 题）
    cognitive_questions = [
        {'question_number': 1, 'category': 'cognitive', 'dimension': 'cognitive', 'question_text': '你清楚电信网络诈骗的常见手段吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 2, 'category': 'cognitive', 'dimension': 'cognitive', 'question_text': '你知道国家反诈中心 App 的主要功能吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 3, 'category': 'cognitive', 'dimension': 'cognitive', 'question_text': '你能准确识别诈骗短信和电话吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 4, 'category': 'cognitive', 'dimension': 'cognitive', 'question_text': '你了解刷单返利是诈骗吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 5, 'category': 'cognitive', 'dimension': 'cognitive', 'question_text': '你知道网络贷款诈骗的常见套路吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 6, 'category': 'cognitive', 'dimension': 'cognitive', 'question_text': '你清楚冒充公检法诈骗的特征吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 7, 'category': 'cognitive', 'dimension': 'cognitive', 'question_text': '你知道虚假投资理财诈骗的模式吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 8, 'category': 'cognitive', 'dimension': 'cognitive', 'question_text': '你了解冒充客服退款诈骗的手法吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 9, 'category': 'cognitive', 'dimension': 'cognitive', 'question_text': '你知道网络交友诱导赌博或投资是诈骗吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 10, 'category': 'cognitive', 'dimension': 'cognitive', 'question_text': '你清楚校园贷诈骗的危害和防范措施吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
    ]
    
    # 行为维度题目（11-20 题）
    behavior_questions = [
        {'question_number': 11, 'category': 'behavior', 'dimension': 'behavior', 'question_text': '你会点击陌生短信中的链接吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 12, 'category': 'behavior', 'dimension': 'behavior', 'question_text': '你会轻易相信陌生人的高额回报承诺吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 13, 'category': 'behavior', 'dimension': 'behavior', 'question_text': '你会向陌生人透露个人身份和银行卡信息吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 14, 'category': 'behavior', 'dimension': 'behavior', 'question_text': '你会参与网络刷单或点赞返利活动吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 15, 'category': 'behavior', 'dimension': 'behavior', 'question_text': '你会通过非正规渠道进行网络贷款吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 16, 'category': 'behavior', 'dimension': 'behavior', 'question_text': '你会随意扫描街边或网络上的不明二维码吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 17, 'category': 'behavior', 'dimension': 'behavior', 'question_text': '你会在陌生网站或 App 中输入银行卡密码和验证码吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 18, 'category': 'behavior', 'dimension': 'behavior', 'question_text': '你会轻易转账给未见过面的网友或所谓“安全账户”吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 19, 'category': 'behavior', 'dimension': 'behavior', 'question_text': '你会下载陌生人推荐的未知来源的投资理财 App 吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 20, 'category': 'behavior', 'dimension': 'behavior', 'question_text': '你会参与网络赌博或相信“稳赚不赔”的投资项目吗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
    ]
    
    # 经历维度题目（21-28 题）
    experience_questions = [
        {'question_number': 21, 'category': 'experience', 'dimension': 'experience', 'question_text': '你或身边人是否曾遭遇过电信网络诈骗？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 22, 'category': 'experience', 'dimension': 'experience', 'question_text': '你是否接到过诈骗电话或短信？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 23, 'category': 'experience', 'dimension': 'experience', 'question_text': '你是否收到过可疑的银行转账或贷款短信？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 24, 'category': 'experience', 'dimension': 'experience', 'question_text': '你是否遇到过陌生人要求提供个人信息或转账？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 25, 'category': 'experience', 'dimension': 'experience', 'question_text': '你是否浏览过可疑的投资理财或赌博网站？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 26, 'category': 'experience', 'dimension': 'experience', 'question_text': '你是否下载过不明来源的金融类 App？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 27, 'category': 'experience', 'dimension': 'experience', 'question_text': '你是否参加过网络刷单或点赞返利活动？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
        {'question_number': 28, 'category': 'experience', 'dimension': 'experience', 'question_text': '你是否因轻信他人而遭受过经济损失？', 'min_score': 1, 'max_score': 5, 'weight': 1.0},
    ]
    
    # 开放性题目（29-30 题）
    open_questions = [
        {'question_number': 29, 'category': 'open', 'dimension': 'open', 'question_text': '请描述你最近收到的一条可疑短信或电话内容', 'min_score': 0, 'max_score': 0, 'weight': 0.0},
        {'question_number': 30, 'category': 'open', 'dimension': 'open', 'question_text': '如果你曾遭遇或险些遭遇诈骗，请简述当时的情形和感受', 'min_score': 0, 'max_score': 0, 'weight': 0.0},
    ]
    
    all_questions = cognitive_questions + behavior_questions + experience_questions + open_questions
    
    # 添加题目
    for q_data in all_questions:
        question = QuestionnaireQuestion(**q_data)
        db.session.add(question)
    
    db.session.commit()
    
    print(f"✓ 成功添加 {len(all_questions)} 道题目到数据库")
    print(f"  - 认知维度：{len(cognitive_questions)} 题")
    print(f"  - 行为维度：{len(behavior_questions)} 题")
    print(f"  - 经历维度：{len(experience_questions)} 题")
    print(f"  - 开放题目：{len(open_questions)} 题")
