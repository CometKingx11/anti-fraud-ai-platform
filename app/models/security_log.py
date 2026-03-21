"""
安全日志模型
记录安全相关事件（异常登录、暴力破解等）
"""

from datetime import datetime
from app import db


class SecurityLog(db.Model):
    """
    安全日志模型
    记录所有安全相关事件
    """
    __tablename__ = 'security_logs'

    id = db.Column(db.Integer, primary_key=True)
    
    # 事件信息
    event_type = db.Column(db.String(50), nullable=False, index=True)  # 事件类型
    event_description = db.Column(db.Text, nullable=False)  # 事件描述
    severity = db.Column(db.String(20), default='medium', index=True)  # 严重程度：low, medium, high, critical
    
    # 涉及用户
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    user_name = db.Column(db.String(50), nullable=True)
    student_id = db.Column(db.String(20), nullable=True)
    
    # 攻击者信息（如果有）
    attacker_ip = db.Column(db.String(50), nullable=True, index=True)  # 攻击 IP
    attacker_user_agent = db.Column(db.String(500), nullable=True)  # 攻击者设备信息
    
    # 请求信息
    request_url = db.Column(db.String(200), nullable=True)
    request_method = db.Column(db.String(10), nullable=True)
    
    # 额外信息
    extra_data = db.Column(db.Text, nullable=True)  # JSON 格式
    
    # 处理状态
    is_handled = db.Column(db.Boolean, default=False, index=True)  # 是否已处理
    handled_by = db.Column(db.String(50), nullable=True)  # 处理人
    handled_at = db.Column(db.DateTime, nullable=True)  # 处理时间
    handle_notes = db.Column(db.Text, nullable=True)  # 处理备注
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关联用户
    user = db.relationship('User', backref=db.backref('security_logs', lazy=True))

    def __repr__(self):
        return f'<SecurityLog {self.id} - {self.event_type} - {self.severity}>'

    @staticmethod
    def log_security_event(event_type, description, severity='medium', **kwargs):
        """
        记录安全事件的便捷方法
        
        Args:
            event_type (str): 事件类型（如：BRUTE_FORCE, SUSPICIOUS_LOGIN, UNAUTHORIZED_ACCESS）
            description (str): 事件描述
            severity (str): 严重程度（low, medium, high, critical）
            **kwargs: 额外的参数
        
        Returns:
            SecurityLog: 创建的日志对象
        """
        from flask import request
        
        log_data = {
            'event_type': event_type,
            'event_description': description,
            'severity': severity,
            'attacker_ip': request.remote_addr if request else None,
            'attacker_user_agent': request.headers.get('User-Agent', '')[:500] if request else None,
            'request_url': request.url if request else None,
            'request_method': request.method if request else None,
        }
        
        # 如果有用户信息
        user = kwargs.get('user')
        if user:
            log_data['user_id'] = user.id
            log_data['user_name'] = user.name
            log_data['student_id'] = user.student_id
        
        # 处理额外数据
        extra_data = kwargs.get('extra_data')
        if extra_data:
            import json
            log_data['extra_data'] = json.dumps(extra_data, ensure_ascii=False)
        
        # 创建并保存日志
        log = SecurityLog(**log_data)
        db.session.add(log)
        db.session.commit()
        
        return log

    # 常用安全事件类型常量
    EVENT_BRUTE_FORCE = 'BRUTE_FORCE'  # 暴力破解
    EVENT_SUSPICIOUS_LOGIN = 'SUSPICIOUS_LOGIN'  # 可疑登录
    EVENT_UNAUTHORIZED_ACCESS = 'UNAUTHORIZED_ACCESS'  # 未授权访问
    EVENT_PASSWORD_SPRAY = 'PASSWORD_SPRAY'  # 密码喷洒攻击
    EVENT_ACCOUNT_LOCKOUT = 'ACCOUNT_LOCKOUT'  # 账号锁定
    EVENT_PRIVILEGE_ESCALATION = 'PRIVILEGE_ESCALATION'  # 权限提升
    EVENT_DATA_EXFILTRATION = 'DATA_EXFILTRATION'  # 数据窃取
    EVENT_MALICIOUS_IP = 'MALICIOUS_IP'  # 恶意 IP

    # 严重程度常量
    SEVERITY_LOW = 'low'
    SEVERITY_MEDIUM = 'medium'
    SEVERITY_HIGH = 'high'
    SEVERITY_CRITICAL = 'critical'
