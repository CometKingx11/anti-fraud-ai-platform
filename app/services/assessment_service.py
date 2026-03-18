# Author: 小土豆233
# Date: 2026-03-16 23:42:18
# LastEditTime: 2026-03-16 23:42:27
# LastEditors: 小土豆233
# Description: 评估服务层
# 处理问卷评估逻辑，包括分数计算、风险分析等功能
# FilePath: flask_anti_project\app\services\assessment_service.py

from datetime import datetime
from app.models.submission import Submission
from app.models.user import User
from app.models.questionnaire import QuestionnaireQuestion
from app.services.ai_analysis_service import AIAnalysisService
from app.services.url_security_service import URLSecurityService
from app import db


class AssessmentService:
    """
    评估服务类
    负责问卷评估的核心业务逻辑
    """

    @staticmethod
    def calculate_scores(answers):
        """
        根据问卷答案计算各维度分数（使用数据库配置的题目）
            
        Args:
            answers (dict): 问卷答案字典，格式为{'q1': 3, 'q2': 5, ...}
            
        Returns:
            dict: 包含各维度分数的字典
        """
        # 从数据库获取题目配置
        cognitive_questions = QuestionnaireQuestion.get_active_questions('cognitive')
        behavior_questions = QuestionnaireQuestion.get_active_questions('behavior')
        experience_questions = QuestionnaireQuestion.get_active_questions('experience')
            
        # 认知维度：正向计分
        cognitive_score = 0
        for q in cognitive_questions:
            answer_key = f'q{q.question_number}'
            if answer_key in answers:
                cognitive_score += int(answers[answer_key]) * q.weight
            
        # 行为风险维度：反向计分（分数越高风险越大）
        behavior_risk = 0
        for q in behavior_questions:
            answer_key = f'q{q.question_number}'
            if answer_key in answers:
                # 反向计分
                score = (q.max_score + q.min_score + 1) - int(answers[answer_key])
                behavior_risk += score * q.weight
            
        # 经历维度：正向计分
        experience_score = 0
        for q in experience_questions:
            answer_key = f'q{q.question_number}'
            if answer_key in answers:
                experience_score += int(answers[answer_key]) * q.weight
            
        # 计算基础总分（满分 100）
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
    def process_questionnaire_submission(user_id, answers, open_texts, uploaded_images, ip_address=None):
        """
        处理问卷提交
            
        Args:
            user_id (int): 用户 ID
            answers (dict): 问卷答案
            open_texts (dict): 开放性问题文本
            uploaded_images (list): 上传的图片路径列表
            ip_address (str): 用户 IP 地址
            
        Returns:
            dict: 评估结果
        """
        # 计算各维度分数（使用数据库配置）
        scores = AssessmentService.calculate_scores(answers)
            
        # 合并开放性文本
        open_text = "\n".join(filter(None, [
            open_texts.get('open1', '').strip(),
            open_texts.get('open2', '').strip()
        ]))
            
        # 【新增】检测开放文本中的 URL
        urls = URLSecurityService.extract_urls_from_text(open_text)
        url_risk_info = []
        url_risk_score = 0
            
        if urls:
            # 批量检测 URL
            url_results = URLSecurityService.batch_check_urls(urls, open_text)
            url_risk_info = [r for r in url_results if r.get('is_risk', False)]
            # 计算 URL 风险加分
            url_risk_score = URLSecurityService.calculate_risk_score(url_results)
            
        # 构建基础评估数据
        assessment_data = {
            'user_id': user_id,
            'base_score': scores['base_score'] + url_risk_score,  # 加上 URL 风险分
            'cognitive': scores['cognitive'],
            'behavior': scores['behavior'],
            'experience': scores['experience'],
            'open_text': open_text,
            'uploaded_images': uploaded_images,
            'ip_address': ip_address,
            'url_risk_info': url_risk_info,  # URL 风险信息
            'url_risk_score': url_risk_score  # URL 风险加分
        }

        # 使用AI进行进一步分析
        ai_service = AIAnalysisService()
        ai_result = ai_service.analyze_assessment(assessment_data)

        # 整合 AI 分析结果
        assessment_data.update({
            'final_score': ai_result.get('final_score', scores['base_score']),
            'risk_level': ai_result.get('risk_level', AssessmentService.determine_risk_level(scores['base_score'])),
            'risk_points': ai_result.get('risk_points', []),
            'analysis': ai_result.get('analysis', '暂无大模型分析结果'),
            'suggestions': ai_result.get('suggestions', []),
            'push_contents': ai_result.get('push_contents', [])
        })

        # 将列表类型的字段转换为 JSON 字符串
        import json
        json_fields = ['risk_points', 'suggestions',
                       'push_contents', 'uploaded_images']
        for field in json_fields:
            if field in assessment_data and isinstance(assessment_data[field], list):
                assessment_data[field] = json.dumps(
                    assessment_data[field], ensure_ascii=False)

        # 保存提交记录
        submission = Submission(**assessment_data)
        db.session.add(submission)
        db.session.commit()

        return assessment_data
