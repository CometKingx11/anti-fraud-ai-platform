"""
日志审计服务
提供统一的日志记录接口
"""

from datetime import datetime, timedelta
from flask import request
from app.models.audit_log import AuditLog
from app.models.security_log import SecurityLog
from app import db


class AuditService:
    """
    审计日志服务
    提供统一的日志记录方法
    """
    
    @staticmethod
    def log_user_action(user, action_type, description, **kwargs):
        """
        记录用户操作日志
        
        Args:
            user: 当前用户对象
            action_type (str): 操作类型
            description (str): 操作描述
            **kwargs: 额外参数
        """
        try:
            return AuditLog.log_action(user, action_type, description, **kwargs)
        except Exception as e:
            # 日志记录失败不应影响主流程
            print(f"记录操作日志失败：{str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def log_security_event(event_type, description, severity='medium', **kwargs):
        """
        记录安全事件日志
        
        Args:
            event_type (str): 事件类型
            description (str): 事件描述
            severity (str): 严重程度
            **kwargs: 额外参数
        """
        try:
            return SecurityLog.log_security_event(event_type, description, severity, **kwargs)
        except Exception as e:
            print(f"记录安全日志失败：{str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def get_user_actions(user_id, days=30, limit=100):
        """
        获取用户最近的操作日志
        
        Args:
            user_id (int): 用户 ID
            days (int): 查询最近 N 天的记录
            limit (int): 返回记录数量限制
        
        Returns:
            list: 操作日志列表
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        logs = AuditLog.query.filter(
            AuditLog.user_id == user_id,
            AuditLog.created_at >= cutoff_date
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()
        
        return logs
    
    @staticmethod
    def get_security_events(severity=None, is_handled=None, limit=100):
        """
        获取安全事件日志
        
        Args:
            severity (str): 严重程度过滤
            is_handled (bool): 处理状态过滤
            limit (int): 返回记录数量限制
        
        Returns:
            list: 安全事件列表
        """
        query = SecurityLog.query
        
        if severity:
            query = query.filter(SecurityLog.severity == severity)
        
        if is_handled is not None:
            query = query.filter(SecurityLog.is_handled == is_handled)
        
        logs = query.order_by(SecurityLog.created_at.desc()).limit(limit).all()
        return logs
    
    @staticmethod
    def get_recent_logs(days=7, limit=500):
        """
        获取最近的操作日志（用于管理员查看）
        
        Args:
            days (int): 查询最近 N 天的记录
            limit (int): 返回记录数量限制
        
        Returns:
            list: 操作日志列表
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        logs = AuditLog.query.filter(
            AuditLog.created_at >= cutoff_date
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()
        
        return logs
    
    @staticmethod
    def mark_security_event_handled(event_id, handled_by, notes=None):
        """
        标记安全事件已处理
        
        Args:
            event_id (int): 事件 ID
            handled_by (str): 处理人
            notes (str): 处理备注
        
        Returns:
            bool: 是否成功标记
        """
        event = SecurityLog.query.get(event_id)
        if not event:
            return False
        
        event.is_handled = True
        event.handled_by = handled_by
        event.handled_at = datetime.utcnow()
        event.handle_notes = notes
        
        db.session.commit()
        return True
    
    @staticmethod
    def get_statistics(days=30):
        """
        获取日志统计信息
        
        Args:
            days (int): 统计最近 N 天的数据
        
        Returns:
            dict: 统计信息
        """
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 操作日志统计
        total_actions = AuditLog.query.filter(
            AuditLog.created_at >= cutoff_date
        ).count()
        
        failed_actions = AuditLog.query.filter(
            AuditLog.created_at >= cutoff_date,
            AuditLog.status == 'failed'
        ).count()
        
        # 安全事件统计
        total_events = SecurityLog.query.filter(
            SecurityLog.created_at >= cutoff_date
        ).count()
        
        critical_events = SecurityLog.query.filter(
            SecurityLog.created_at >= cutoff_date,
            SecurityLog.severity == 'critical'
        ).count()
        
        high_events = SecurityLog.query.filter(
            SecurityLog.created_at >= cutoff_date,
            SecurityLog.severity == 'high'
        ).count()
        
        medium_events = SecurityLog.query.filter(
            SecurityLog.created_at >= cutoff_date,
            SecurityLog.severity == 'medium'
        ).count()
        
        low_events = SecurityLog.query.filter(
            SecurityLog.created_at >= cutoff_date,
            SecurityLog.severity == 'low'
        ).count()
        
        unhandled_events = SecurityLog.query.filter(
            SecurityLog.created_at >= cutoff_date,
            SecurityLog.is_handled == False
        ).count()
        
        # 操作趋势（按天统计）
        operation_trend = db.session.query(
            func.date(AuditLog.created_at).label('date'),
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= cutoff_date
        ).group_by(
            func.date(AuditLog.created_at)
        ).order_by(
            func.date(AuditLog.created_at)
        ).all()
        
        operation_trend_labels = [str(d[0]) for d in operation_trend]
        operation_trend_data = [d[1] for d in operation_trend]
        
        # 安全事件类型分布
        event_types = db.session.query(
            SecurityLog.event_type,
            func.count(SecurityLog.id).label('count')
        ).filter(
            SecurityLog.created_at >= cutoff_date
        ).group_by(
            SecurityLog.event_type
        ).all()
        
        security_event_types_labels = [et[0] for et in event_types]
        security_event_types_data = [et[1] for et in event_types]
        
        # 活跃用户 TOP 10
        active_users = db.session.query(
            AuditLog.user_name,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= cutoff_date,
            AuditLog.user_name.isnot(None)
        ).group_by(
            AuditLog.user_name
        ).order_by(
            func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        active_users_labels = [u[0] or '未知用户' for u in active_users]
        active_users_data = [u[1] for u in active_users]
        
        return {
            'total_operations': total_actions,
            'failed_operations': failed_actions,
            'total_security_events': total_events,
            'severity_critical': critical_events,
            'severity_high': high_events,
            'severity_medium': medium_events,
            'severity_low': low_events,
            'unhandled_events': unhandled_events,
            'operation_trend_labels': operation_trend_labels,
            'operation_trend_data': operation_trend_data,
            'security_event_types_labels': security_event_types_labels,
            'security_event_types_data': security_event_types_data,
            'active_users_labels': active_users_labels,
            'active_users_data': active_users_data
        }
    
    @staticmethod
    def get_period_comparison(days_current=7, days_previous=7):
        """
        获取时间段对比数据（本周 vs 上周）
        
        Args:
            days_current (int): 当前时间段天数
            days_previous (int): 对比时间段天数
        
        Returns:
            dict: 对比数据
        """
        from sqlalchemy import func
        
        now = datetime.utcnow()
        current_start = now - timedelta(days=days_current)
        previous_start = current_start - timedelta(days=days_previous)
        
        # 当前时间段统计
        current_ops = AuditLog.query.filter(
            AuditLog.created_at >= current_start,
            AuditLog.created_at <= now
        ).count()
        
        current_events = SecurityLog.query.filter(
            SecurityLog.created_at >= current_start,
            SecurityLog.created_at <= now
        ).count()
        
        # 上一时间段统计
        previous_ops = AuditLog.query.filter(
            AuditLog.created_at >= previous_start,
            AuditLog.created_at < current_start
        ).count()
        
        previous_events = SecurityLog.query.filter(
            SecurityLog.created_at >= previous_start,
            SecurityLog.created_at < current_start
        ).count()
        
        # 计算变化率
        ops_change = ((current_ops - previous_ops) / previous_ops * 100) if previous_ops > 0 else 0
        events_change = ((current_events - previous_events) / previous_events * 100) if previous_events > 0 else 0
        
        return {
            'current_operations': current_ops,
            'previous_operations': previous_ops,
            'operations_change_percent': round(ops_change, 2),
            'current_events': current_events,
            'previous_events': previous_events,
            'events_change_percent': round(events_change, 2)
        }
    
    @staticmethod
    def get_user_behavior_analysis(days=30):
        """
        获取用户行为分析数据
        
        Args:
            days (int): 分析最近 N 天的数据
        
        Returns:
            dict: 用户行为分析数据
        """
        from sqlalchemy import func
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 登录时间分布（按小时统计）
        login_hours = db.session.query(
            func.hour(AuditLog.created_at).label('hour'),
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= cutoff_date,
            AuditLog.action_type == 'LOGIN'
        ).group_by(
            func.hour(AuditLog.created_at)
        ).order_by(
            func.hour(AuditLog.created_at)
        ).all()
        
        hour_labels = [f"{h[0]:02d}:00" for h in login_hours]
        hour_data = [h[1] for h in login_hours]
        
        # 操作频率 TOP 10 用户
        user_freq = db.session.query(
            AuditLog.user_name,
            AuditLog.user_id,
            func.count(AuditLog.id).label('count'),
            func.max(AuditLog.created_at).label('last_active')
        ).filter(
            AuditLog.created_at >= cutoff_date,
            AuditLog.user_name.isnot(None)
        ).group_by(
            AuditLog.user_id, AuditLog.user_name
        ).order_by(
            func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        top_users = [{
            'name': u.user_name or '未知用户',
            'user_id': u.user_id,
            'count': u.count,
            'last_active': str(u.last_active)
        } for u in user_freq]
        
        # 操作类型分布
        action_types = db.session.query(
            AuditLog.action_type,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= cutoff_date
        ).group_by(
            AuditLog.action_type
        ).order_by(
            func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        action_labels = [a.action_type for a in action_types]
        action_data = [a.count for a in action_types]
        
        return {
            'login_hour_labels': hour_labels,
            'login_hour_data': hour_data,
            'top_users': top_users,
            'action_type_labels': action_labels,
            'action_type_data': action_data
        }
    
    @staticmethod
    def get_question_statistics(days=30):
        """
        获取问卷题目正确率统计
        
        Args:
            days (int): 统计最近 N 天的数据
        
        Returns:
            dict: 题目正确率统计
        """
        from app.models.submission import Submission
        from sqlalchemy import func, text
        import json
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取所有提交记录
        submissions = Submission.query.filter(
            Submission.submitted_at >= cutoff_date
        ).all()
        
        if not submissions:
            return {
                'question_stats': [],
                'total_submissions': 0
            }
        
        # 统计每道题的得分情况
        question_scores = {}
        
        for submission in submissions:
            answers = submission.answers
            if not answers:
                continue
            
            try:
                # answers 可能是 JSON 字符串或字典
                if isinstance(answers, str):
                    answers_data = json.loads(answers)
                else:
                    answers_data = answers
                
                for answer in answers_data:
                    question_id = answer.get('question_id')
                    score = answer.get('score', 0)
                    max_score = answer.get('max_score', 0)
                    question_text = answer.get('question_text', f'题目{question_id}')
                    
                    if question_id not in question_scores:
                        question_scores[question_id] = {
                            'question_id': question_id,
                            'question_text': question_text[:50],
                            'total_score': 0,
                            'max_score': max_score,
                            'count': 0
                        }
                    
                    question_scores[question_id]['total_score'] += score
                    question_scores[question_id]['count'] += 1
            except Exception as e:
                continue
        
        # 计算平均正确率
        question_stats = []
        for q_id, stats in question_scores.items():
            avg_score_rate = (stats['total_score'] / (stats['max_score'] * stats['count']) * 100) if stats['max_score'] > 0 and stats['count'] > 0 else 0
            question_stats.append({
                'question_id': q_id,
                'question_text': stats['question_text'],
                'avg_score_rate': round(avg_score_rate, 2),
                'total_attempts': stats['count'],
                'avg_score': round(stats['total_score'] / stats['count'], 2) if stats['count'] > 0 else 0,
                'max_score': stats['max_score']
            })
        
        # 按正确率排序
        question_stats.sort(key=lambda x: x['avg_score_rate'])
        
        return {
            'question_stats': question_stats[:20],  # 只返回最低正确率的 20 道题
            'total_submissions': len(submissions)
        }


# 便捷的装饰器，用于自动记录操作日志
def log_action(action_type, description_template):
    """
    装饰器：自动记录操作日志
    
    Usage:
        @log_action('EXPORT_DATA', '导出数据：{report_type}')
        def export_data(report_type):
            ...
    
    Args:
        action_type (str): 操作类型
        description_template (str): 描述模板，支持格式化
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            from flask_login import current_user
            
            # 执行原函数
            result = f(*args, **kwargs)
            
            # 记录日志
            try:
                # 格式化描述
                description = description_template.format(**kwargs)
                
                # 记录成功日志
                AuditService.log_user_action(
                    current_user._get_current_object() if current_user.is_authenticated else None,
                    action_type,
                    description,
                    status='success'
                )
            except Exception as e:
                # 记录失败日志
                AuditService.log_user_action(
                    current_user._get_current_object() if current_user.is_authenticated else None,
                    action_type,
                    f'{description_template} - 失败',
                    status='failed',
                    error_message=str(e)
                )
            
            return result
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator
