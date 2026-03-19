"""
AI 统计报告服务
基于千问 AI 生成整体统计分析报告
"""

import json
from datetime import datetime
from flask import current_app
from dashscope import Generation
from app.models.submission import Submission
from app.models.user import User
from sqlalchemy import func


class AIReportService:
    """
    AI 统计报告服务类
    负责统计所有用户提交数据并生成 AI 分析报告
    """

    def generate_statistical_report(self, start_date=None, end_date=None, risk_level=None):
        """
        生成统计报告

        Args:
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            risk_level: 风险等级（可选）

        Returns:
            dict: 统计数据和 AI 分析报告
        """
        # 1. 收集统计数据
        statistics = self._collect_statistics(start_date, end_date, risk_level)
        
        # 2. 使用 AI 生成分析报告
        ai_analysis = self._generate_ai_analysis(statistics)
        
        # 3. 合并结果
        report = {
            'statistics': statistics,
            'ai_analysis': ai_analysis,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return report

    def _collect_statistics(self, start_date=None, end_date=None, risk_level=None):
        """
        收集统计数据

        Args:
            start_date: 开始日期
            end_date: 结束日期
            risk_level: 风险等级

        Returns:
            dict: 统计数据
        """
        # 基础查询
        query = Submission.query.join(User)
        
        # 应用筛选条件
        if start_date:
            query = query.filter(Submission.submitted_at >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Submission.submitted_at <= datetime.strptime(end_date, '%Y-%m-%d'))
        if risk_level:
            query = query.filter(Submission.risk_level == risk_level)
        
        # 只统计有效数据
        query = query.filter(Submission.is_valid == True)
        
        all_submissions = query.all()
        
        # 基本统计
        total_submissions = len(all_submissions)
        total_students = User.query.filter_by(role='student').count()
        
        # 风险等级分布
        risk_distribution = db.session.query(
            Submission.risk_level,
            func.count(Submission.id)
        ).filter(Submission.is_valid == True)
        
        if start_date:
            risk_distribution = risk_distribution.filter(Submission.submitted_at >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            risk_distribution = risk_distribution.filter(Submission.submitted_at <= datetime.strptime(end_date, '%Y-%m-%d'))
        if risk_level:
            risk_distribution = risk_distribution.filter(Submission.risk_level == risk_level)
        
        risk_distribution = risk_distribution.group_by(Submission.risk_level).all()
        
        risk_stats = {
            '极高风险': 0,
            '高风险': 0,
            '中风险': 0,
            '低风险': 0
        }
        for level, count in risk_distribution:
            if level in risk_stats:
                risk_stats[level] = count
        
        # 分数统计
        scores = [s.final_score for s in all_submissions if s.final_score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        # 维度分析
        cognitive_scores = [s.cognitive for s in all_submissions if s.cognitive is not None]
        behavior_scores = [s.behavior for s in all_submissions if s.behavior is not None]
        experience_scores = [s.experience for s in all_submissions if s.experience is not None]
        
        avg_cognitive = sum(cognitive_scores) / len(cognitive_scores) if cognitive_scores else 0
        avg_behavior = sum(behavior_scores) / len(behavior_scores) if behavior_scores else 0
        avg_experience = sum(experience_scores) / len(experience_scores) if experience_scores else 0
        
        # 高频风险点分析
        risk_points_freq = {}
        for s in all_submissions:
            if s.risk_points:
                try:
                    points = json.loads(s.risk_points)
                    for point in points:
                        risk_points_freq[point] = risk_points_freq.get(point, 0) + 1
                except:
                    pass
        
        # 按出现频率排序
        top_risk_points = sorted(risk_points_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 提交趋势（按日期）
        submission_trend = db.session.query(
            func.date(Submission.submitted_at),
            func.count(Submission.id)
        ).filter(Submission.is_valid == True)
        
        if start_date:
            submission_trend = submission_trend.filter(Submission.submitted_at >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            submission_trend = submission_trend.filter(Submission.submitted_at <= datetime.strptime(end_date, '%Y-%m-%d'))
        
        submission_trend = submission_trend.group_by(func.date(Submission.submitted_at)).order_by(
            func.date(Submission.submitted_at)
        ).all()
        
        trend_data = [{'date': str(date), 'count': count} for date, count in submission_trend]
        
        return {
            'total_submissions': total_submissions,
            'total_students': total_students,
            'participation_rate': f"{(total_submissions / total_students * 100) if total_students > 0 else 0:.1f}%",
            'risk_distribution': risk_stats,
            'score_stats': {
                'average': f"{avg_score:.1f}",
                'max': max_score,
                'min': min_score
            },
            'dimension_analysis': {
                'cognitive': f"{avg_cognitive:.1f}/40",
                'behavior': f"{avg_behavior:.1f}/40",
                'experience': f"{avg_experience:.1f}/20"
            },
            'top_risk_points': top_risk_points,
            'submission_trend': trend_data
        }

    def _generate_ai_analysis(self, statistics):
        """
        使用 AI 生成分析报告

        Args:
            statistics: 统计数据

        Returns:
            str: AI 生成的分析报告
        """
        api_key = current_app.config.get('DASHSCOPE_API_KEY')
        
        if not api_key:
            return self._get_rule_based_analysis(statistics)
        
        # 构建提示词
        prompt = self._build_report_prompt(statistics)
        
        try:
            # 调用千问 API
            response = Generation.call(
                model='qwen-plus',
                prompt=prompt,
                api_key=api_key,
                result_format='message'
            )
            
            # 提取 AI 生成的内容
            ai_content = response.output.choices[0].message.content
            return ai_content
            
        except Exception as e:
            print(f"AI 报告生成失败：{str(e)}")
            return self._get_rule_based_analysis(statistics)

    def _build_report_prompt(self, statistics):
        """
        构建 AI 报告提示词

        Args:
            statistics: 统计数据

        Returns:
            str: 提示词
        """
        prompt = f"""
你是反诈风险评估专家，请根据以下统计数据生成一份专业的分析报告：

【基本数据】
- 总提交次数：{statistics['total_submissions']}
- 学生总数：{statistics['total_students']}
- 参与率：{statistics['participation_rate']}

【风险等级分布】
- 极高风险：{statistics['risk_distribution']['极高风险']} 人
- 高风险：{statistics['risk_distribution']['高风险']} 人
- 中风险：{statistics['risk_distribution']['中风险']} 人
- 低风险：{statistics['risk_distribution']['低风险']} 人

【分数统计】
- 平均分：{statistics['score_stats']['average']}
- 最高分：{statistics['score_stats']['max']}
- 最低分：{statistics['score_stats']['min']}

【维度分析】
- 认知维度平均：{statistics['dimension_analysis']['cognitive']}
- 行为维度平均：{statistics['dimension_analysis']['behavior']}
- 经历维度平均：{statistics['dimension_analysis']['experience']}

【高频风险点 TOP10】
{chr(10).join([f"- {point}: {count}次" for point, count in statistics['top_risk_points']])}

请生成一份 800-1000 字的分析报告，包括：
1. 整体风险评估
2. 主要风险特征分析
3. 高风险群体画像
4. 存在的问题
5. 针对性建议措施

要求：
- 使用专业、客观的语言
- 数据准确、分析深入
- 建议具体、可操作
- 分段清晰、逻辑严谨
"""
        return prompt

    def _get_rule_based_analysis(self, statistics):
        """
        基于规则的分析报告（备用方案）

        Args:
            statistics: 统计数据

        Returns:
            str: 分析报告
        """
        total = statistics['total_submissions']
        high_risk = statistics['risk_distribution']['极高风险'] + statistics['risk_distribution']['高风险']
        high_risk_rate = (high_risk / total * 100) if total > 0 else 0
        
        report = f"""
【反诈风险评估统计分析报告】

一、整体情况
本次统计共收集 {total} 份有效问卷，参与学生 {statistics['total_students']} 人，参与率 {statistics['participation_rate']}。
平均风险得分为 {statistics['score_stats']['average']} 分，最高分 {statistics['score_stats']['max']} 分，最低分 {statistics['score_stats']['min']} 分。

二、风险等级分布
高风险及以上学生 {high_risk} 人，占比 {high_risk_rate:.1f}%。
其中：极高风险 {statistics['risk_distribution']['极高风险']} 人，高风险 {statistics['risk_distribution']['高风险']} 人，
中风险 {statistics['risk_distribution']['中风险']} 人，低风险 {statistics['risk_distribution']['低风险']} 人。

三、维度分析
认知维度平均得分 {statistics['dimension_analysis']['cognitive']}，行为维度平均得分 {statistics['dimension_analysis']['behavior']}，
经历维度平均得分 {statistics['dimension_analysis']['experience']}。

四、主要风险点
高频风险点包括：{', '.join([point for point, _ in statistics['top_risk_points'][:5]])}

五、建议措施
1. 加强反诈知识宣传教育
2. 针对高风险学生开展重点帮扶
3. 定期组织反诈知识测试
4. 建立预警机制，及时发现和干预
"""
        return report


# 需要导入 db
from app import db
