"""
操作日志模型
记录用户的关键操作，用于审计和追踪
"""

from datetime import datetime
from app import db


class AuditLog(db.Model):
    """
    操作日志模型
    记录所有关键操作（登录、修改密码、导出数据等）
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    
    # 操作人信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    user_name = db.Column(db.String(50), nullable=True)  # 冗余存储，防止用户被删除后无法查看
    student_id = db.Column(db.String(20), nullable=True)  # 学号
    
    # 操作信息
    action_type = db.Column(db.String(50), nullable=False, index=True)  # 操作类型
    action_description = db.Column(db.Text, nullable=False)  # 操作描述
    target_type = db.Column(db.String(50), nullable=True)  # 操作对象类型（如：User, Submission）
    target_id = db.Column(db.Integer, nullable=True)  # 操作对象 ID
    
    # 请求信息
    ip_address = db.Column(db.String(50), nullable=True)  # IP 地址
    user_agent = db.Column(db.String(500), nullable=True)  # 浏览器/设备信息
    request_method = db.Column(db.String(10), nullable=True)  # 请求方法（GET/POST 等）
    request_url = db.Column(db.String(200), nullable=True)  # 请求 URL
    
    # 操作结果
    status = db.Column(db.String(20), default='success', index=True)  # success, failed, error
    error_message = db.Column(db.Text, nullable=True)  # 错误信息（如果有）
    
    # 额外数据（JSON 格式）
    extra_data = db.Column(db.Text, nullable=True)  # 额外的操作数据
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关联用户
    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))

    def __repr__(self):
        return f'<AuditLog {self.id} - {self.user_name} - {self.action_type}>'

    @staticmethod
    def log_action(user, action_type, description, **kwargs):
        """
        记录操作日志的便捷方法
        
        Args:
            user: 当前用户对象
            action_type (str): 操作类型（如：LOGIN, UPDATE_PASSWORD, EXPORT_DATA）
            description (str): 操作描述
            **kwargs: 额外的参数（target_type, target_id, status, error_message, extra_data）
        
        Returns:
            AuditLog: 创建的日志对象
        """
        from flask import request
        
        # 准备基础数据
        log_data = {
            'user_id': user.id if user else None,
            'user_name': user.name if user else 'Anonymous',
            'student_id': user.student_id if user else None,
            'action_type': action_type,
            'action_description': description,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent', '')[:500] if request else None,
            'request_method': request.method if request else None,
            'request_url': request.url if request else None,
            'status': kwargs.get('status', 'success'),
            'error_message': kwargs.get('error_message'),
            'target_type': kwargs.get('target_type'),
            'target_id': kwargs.get('target_id'),
        }
        
        # 处理额外数据（转换为 JSON）
        extra_data = kwargs.get('extra_data')
        if extra_data:
            import json
            log_data['extra_data'] = json.dumps(extra_data, ensure_ascii=False)
        
        # 创建并保存日志
        log = AuditLog(**log_data)
        db.session.add(log)
        db.session.commit()
        
        return log

    # 常用操作类型常量
    ACTION_LOGIN = 'LOGIN'
    ACTION_LOGOUT = 'LOGOUT'
    ACTION_UPDATE_PASSWORD = 'UPDATE_PASSWORD'
    ACTION_RESET_PASSWORD = 'RESET_PASSWORD'
    ACTION_CREATE_USER = 'CREATE_USER'
    ACTION_UPDATE_USER = 'UPDATE_USER'
    ACTION_DELETE_USER = 'DELETE_USER'
    ACTION_EXPORT_DATA = 'EXPORT_DATA'
    ACTION_IMPORT_DATA = 'IMPORT_DATA'
    ACTION_VIEW_REPORT = 'VIEW_REPORT'
    ACTION_SUBMIT_QUESTIONNAIRE = 'SUBMIT_QUESTIONNAIRE'
    ACTION_UPDATE_CONFIG = 'UPDATE_CONFIG'
