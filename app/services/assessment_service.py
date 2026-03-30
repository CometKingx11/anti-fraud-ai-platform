# Author: 小土豆 233
# Description: 评估服务层
# 处理问卷评估逻辑，包括分数计算、风险分析等功能

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
        根据分数确定风险等级（使用配置的阈值）

        Args:
            score (int): 评估分数

        Returns:
            str: 风险等级
        """
        # 从配置中读取阈值，如果不存在则使用默认值
        from app.models.questionnaire import QuestionnaireConfig
        threshold_low = QuestionnaireConfig.get_int_config('threshold_low', 30)
        threshold_mid = QuestionnaireConfig.get_int_config('threshold_mid', 55)
        threshold_high = QuestionnaireConfig.get_int_config('threshold_high', 80)
        
        if score <= threshold_low:
            return "低风险"
        elif score <= threshold_mid:
            return "中风险"
        elif score <= threshold_high:
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
        
        # 【新增】检查是否启用 AI 智能分析
        from app.models.questionnaire import QuestionnaireConfig
        enable_ai_analysis = QuestionnaireConfig.get_config('enable_ai_analysis', '1') == '1'
                
        if enable_ai_analysis:
            # 使用 AI 进行进一步分析
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
        else:
            # AI 分析已禁用，使用基础规则评估
            assessment_data.update({
                'final_score': scores['base_score'] + url_risk_score,
                'risk_level': AssessmentService.determine_risk_level(scores['base_score'] + url_risk_score),
                'risk_points': [],  # 不提供风险点
                'analysis': 'AI 智能分析已禁用，仅使用基础评分规则',
                'suggestions': [],  # 不提供建议
                'push_contents': []  # 不提供推送内容
            })

        # 将列表类型的字段转换为 JSON 字符串
        import json
        json_fields = ['risk_points', 'suggestions',
                       'push_contents', 'uploaded_images', 'url_risk_info']
        for field in json_fields:
            if field in assessment_data and isinstance(assessment_data[field], list):
                assessment_data[field] = json.dumps(
                    assessment_data[field], ensure_ascii=False)

        # 保存提交记录
        submission = Submission(**assessment_data)
        db.session.add(submission)
        db.session.commit()
        
        # 【新增】检查是否需要发送风险预警邮件
        AssessmentService._send_risk_warning_email_if_needed(
            user_id=user_id,
            risk_level=assessment_data['risk_level'],
            total_score=assessment_data['final_score']
        )

        return assessment_data
    
    @staticmethod
    def _send_risk_warning_email_if_needed(user_id, risk_level, total_score):
        """
        检查是否需要发送风险预警邮件（高风险/极高风险时发送）
        
        Args:
            user_id (int): 用户 ID
            risk_level (str): 风险等级
            total_score (int): 风险总分
        """
        try:
            # 只在高风险或极高风险时发送邮件
            if risk_level not in ['高风险', '极高风险']:
                return
            
            # 获取用户信息
            user = User.query.get(user_id)
            if not user or not user.email:
                # 用户不存在或没有邮箱，不发送邮件
                return
            
            # 发送邮件
            from app.services.email_service import EmailService
            EmailService.send_risk_warning_email(
                user_email=user.email,
                user_name=user.name,
                risk_level=risk_level,
                total_score=total_score
            )
            
            print(f"✓ 已发送风险预警邮件给 {user.email}（风险等级：{risk_level}）")
            
        except Exception as e:
            # 邮件发送失败不影响主流程，仅记录日志
            print(f"⚠️ 发送风险预警邮件失败：{str(e)}")
