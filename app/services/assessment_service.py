'''
Author: 小土豆233
Date: 2026-03-16 23:42:18
LastEditTime: 2026-03-16 23:42:27
LastEditors: 小土豆233
Description: 评估服务层
处理问卷评估逻辑，包括分数计算、风险分析等功能
FilePath: \flask_anti_project\app\__init__.py
'''

from datetime import datetime
from app.models.submission import Submission
from app.models.user import User
from app.services.ai_analysis_service import AIAnalysisService
from app import db


class AssessmentService:
    """
    评估服务类
    负责问卷评估的核心业务逻辑
    """

    @staticmethod
    def calculate_scores(answers):
        """
        根据问卷答案计算各维度分数

        Args:
            answers (dict): 问卷答案字典，格式为{'q1': 3, 'q2': 5, ...}

        Returns:
            dict: 包含各维度分数的字典
        """
        # 认知维度：题目1-10，分数越高越安全
        cognitive_score = sum(answers.get(f'q{i}', 0) for i in range(1, 11))
        cognitive_score = min(cognitive_score, 50)  # 最大值限制为50

        # 行为风险维度：题目11-20，分数越高风险越大
        behavior_risk = sum(6 - answers.get(f'q{i}', 0) for i in range(11, 21))

        # 经历维度：题目21-28，分数越高风险越大
        experience_score = sum(answers.get(f'q{i}', 0) for i in range(21, 29))

        # 计算基础总分（满分100）
        base_score = round(
            (cognitive_score / 50.0) * 40 +
            (behavior_risk / 50.0) * 40 +
            (experience_score / 40.0) * 20
        )

        return {
            'cognitive': round((cognitive_score / 50.0) * 40),
            'behavior': round((behavior_risk / 50.0) * 40),
            'experience': round((experience_score / 40.0) * 20),
            'base_score': base_score
        }

    @staticmethod
    def determine_risk_level(score):
        """
        根据分数确定风险等级

        Args:
            score (int): 评估分数

        Returns:
            str: 风险等级
        """
        if score <= 30:
            return "低风险"
        elif score <= 55:
            return "中风险"
        elif score <= 80:
            return "高风险"
        else:
            return "极高风险"

    @staticmethod
    def process_questionnaire_submission(user_id, answers, open_texts, uploaded_images):
        """
        处理问卷提交

        Args:
            user_id (int): 用户ID
            answers (dict): 问卷答案
            open_texts (dict): 开放性问题文本
            uploaded_images (list): 上传的图片路径列表

        Returns:
            dict: 评估结果
        """
        # 计算各维度分数
        scores = AssessmentService.calculate_scores(answers)

        # 合并开放性文本
        open_text = "\n".join(filter(None, [
            open_texts.get('open1', '').strip(),
            open_texts.get('open2', '').strip()
        ]))

        # 构建基础评估数据
        assessment_data = {
            'user_id': user_id,
            'base_score': scores['base_score'],
            'cognitive': scores['cognitive'],
            'behavior': scores['behavior'],
            'experience': scores['experience'],
            'open_text': open_text,
            'uploaded_images': uploaded_images
        }

        # 使用AI进行进一步分析
        ai_service = AIAnalysisService()
        ai_result = ai_service.analyze_assessment(assessment_data)

        # 整合AI分析结果
        assessment_data.update({
            'final_score': ai_result.get('final_score', scores['base_score']),
            'risk_level': ai_result.get('risk_level', AssessmentService.determine_risk_level(scores['base_score'])),
            'risk_points': ai_result.get('risk_points', []),
            'analysis': ai_result.get('analysis', '暂无大模型分析结果'),
            'suggestions': ai_result.get('suggestions', []),
            'push_contents': ai_result.get('push_contents', [])
        })

        # 保存提交记录
        submission = Submission(**assessment_data)
        db.session.add(submission)
        db.session.commit()

        return assessment_data
