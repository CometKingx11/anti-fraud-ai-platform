"""直接添加题目到数据库"""
import sqlite3

# 连接到数据库
conn = sqlite3.connect('instance/anti_fraud_dev.db')
cursor = conn.cursor()

# 删除所有现有题目
cursor.execute('DELETE FROM questionnaire_questions')

# 添加认知维度题目
cognitive = [
    (1, 'cognitive', 'cognitive', '你清楚电信网络诈骗的常见手段吗？', 1, 5, 1.0),
    (2, 'cognitive', 'cognitive', '你知道国家反诈中心 App 的主要功能吗？', 1, 5, 1.0),
    (3, 'cognitive', 'cognitive', '你能准确识别诈骗短信和电话吗？', 1, 5, 1.0),
    (4, 'cognitive', 'cognitive', '你了解刷单返利是诈骗吗？', 1, 5, 1.0),
    (5, 'cognitive', 'cognitive', '你知道网络贷款诈骗的常见套路吗？', 1, 5, 1.0),
    (6, 'cognitive', 'cognitive', '你清楚冒充公检法诈骗的特征吗？', 1, 5, 1.0),
    (7, 'cognitive', 'cognitive', '你知道虚假投资理财诈骗的模式吗？', 1, 5, 1.0),
    (8, 'cognitive', 'cognitive', '你了解冒充客服退款诈骗的手法吗？', 1, 5, 1.0),
    (9, 'cognitive', 'cognitive', '你知道网络交友诱导赌博或投资是诈骗吗？', 1, 5, 1.0),
    (10, 'cognitive', 'cognitive', '你清楚校园贷诈骗的危害和防范措施吗？', 1, 5, 1.0),
]

# 添加行为维度题目
behavior = [
    (11, 'behavior', 'behavior', '你会点击陌生短信中的链接吗？', 1, 5, 1.0),
    (12, 'behavior', 'behavior', '你会轻易相信陌生人的高额回报承诺吗？', 1, 5, 1.0),
    (13, 'behavior', 'behavior', '你会向陌生人透露个人身份和银行卡信息吗？', 1, 5, 1.0),
    (14, 'behavior', 'behavior', '你会参与网络刷单或点赞返利活动吗？', 1, 5, 1.0),
    (15, 'behavior', 'behavior', '你会通过非正规渠道进行网络贷款吗？', 1, 5, 1.0),
    (16, 'behavior', 'behavior', '你会随意扫描街边或网络上的不明二维码吗？', 1, 5, 1.0),
    (17, 'behavior', 'behavior', '你会在陌生网站或 App 中输入银行卡密码和验证码吗？', 1, 5, 1.0),
    (18, 'behavior', 'behavior', '你会轻易转账给未见过面的网友或所谓“安全账户”吗？', 1, 5, 1.0),
    (19, 'behavior', 'behavior', '你会下载陌生人推荐的未知来源的投资理财 App 吗？', 1, 5, 1.0),
    (20, 'behavior', 'behavior', '你会参与网络赌博或相信“稳赚不赔”的投资项目吗？', 1, 5, 1.0),
]

# 添加经历维度题目
experience = [
    (21, 'experience', 'experience', '你或身边人是否曾遭遇过电信网络诈骗？', 1, 5, 1.0),
    (22, 'experience', 'experience', '你是否接到过诈骗电话或短信？', 1, 5, 1.0),
    (23, 'experience', 'experience', '你是否收到过可疑的银行转账或贷款短信？', 1, 5, 1.0),
    (24, 'experience', 'experience', '你是否遇到过陌生人要求提供个人信息或转账？', 1, 5, 1.0),
    (25, 'experience', 'experience', '你是否浏览过可疑的投资理财或赌博网站？', 1, 5, 1.0),
    (26, 'experience', 'experience', '你是否下载过不明来源的金融类 App？', 1, 5, 1.0),
    (27, 'experience', 'experience', '你是否参加过网络刷单或点赞返利活动？', 1, 5, 1.0),
    (28, 'experience', 'experience', '你是否因轻信他人而遭受过经济损失？', 1, 5, 1.0),
]

# 添加开放性题目
open_q = [
    (29, 'open', 'open', '请描述你最近收到的一条可疑短信或电话内容', 0, 0, 0.0),
    (30, 'open', 'open', '如果你曾遭遇或险些遭遇诈骗，请简述当时的情形和感受', 0, 0, 0.0),
]

all_questions = cognitive + behavior + experience + open_q

# 插入数据
for q in all_questions:
    cursor.execute('''
        INSERT INTO questionnaire_questions 
        (question_number, category, dimension, question_text, min_score, max_score, weight, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    ''', q)

conn.commit()
print(f"✓ 成功添加 {len(all_questions)} 道题目到数据库")
print(f"  - 认知维度：{len(cognitive)} 题")
print(f"  - 行为维度：{len(behavior)} 题")
print(f"  - 经历维度：{len(experience)} 题")
print(f"  - 开放题目：{len(open_q)} 题")

# 验证
cursor.execute('SELECT COUNT(*) FROM questionnaire_questions')
count = cursor.fetchone()[0]
print(f"\n数据库验证：共有 {count} 道题目")

conn.close()
