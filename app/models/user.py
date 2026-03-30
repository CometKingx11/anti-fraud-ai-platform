# Author: 小土豆 233
# Description: 用户数据模型，定义了系统中的用户实体
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """
    用户模型
    继承UserMixin以支持Flask-Login功能
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True,
                           nullable=False, index=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """
        设置用户密码（哈希加密）

        Args:
            password (str): 明文密码
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        验证密码

        Args:
            password (str): 待验证的明文密码

        Returns:
            bool: 密码是否正确
        """
        return check_password_hash(self.password_hash, password)

    def is_disabled(self):
        """
        检查用户是否被禁用

        Returns:
            bool: 如果用户被禁用返回 True，否则返回 False
        """
        return not self.is_active

    def update_last_login(self):
        """
        更新最后登录时间
        """
        from app import db
        self.last_login = datetime.utcnow()
        db.session.commit()

    def get_id(self):
        """
        获取用户ID（Flask-Login要求）

        Returns:
            str: 用户ID字符串
        """
        return str(self.id)

    def __repr__(self):
        """
        用户对象的字符串表示

        Returns:
            str: 用户信息字符串
        """
        return f'<User {self.student_id}>'

    @classmethod
    def get_by_student_id(cls, student_id):
        """
        根据学号获取用户

        Args:
            student_id (str): 学号

        Returns:
            User: 用户对象，若不存在返回None
        """
        return cls.query.filter_by(student_id=student_id).first()

    @classmethod
    def create_user(cls, student_id, password, role='student', name=None):
        """
        创建新用户
    
        Args:
            student_id (str): 学号
            password (str): 明文密码
            role (str): 用户角色，默认为'student'
            name (str): 用户姓名，默认为 None
    
        Returns:
            User: 新创建的用户对象
        """
        user = cls(
            student_id=student_id,
            name=name,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @classmethod
    def update_user(cls, user_id, **kwargs):
        """
        更新用户信息
    
        Args:
            user_id (int): 用户 ID
            **kwargs: 要更新的字段
    
        Returns:
            User: 更新后的用户对象，失败返回 None
        """
        user = cls.query.get(user_id)
        if not user:
            return None
    
        # 允许更新的字段
        allowed_fields = ['name', 'email', 'role', 'is_active']
        for field in allowed_fields:
            if field in kwargs:
                setattr(user, field, kwargs[field])
    
        # 如果更新了密码
        if 'password' in kwargs and kwargs['password']:
            user.set_password(kwargs['password'])
    
        db.session.commit()
        return user
    
    @classmethod
    def delete_user(cls, user_id):
        """
        删除用户
    
        Args:
            user_id (int): 用户 ID
    
        Returns:
            bool: 是否删除成功
        """
        user = cls.query.get(user_id)
        if not user:
            return False
    
        db.session.delete(user)
        db.session.commit()
        return True
    
    @classmethod
    def reset_password(cls, student_id, new_password):
        """
        重置用户密码
    
        Args:
            student_id (str): 学号
            new_password (str): 新密码
    
        Returns:
            bool: 是否重置成功
        """
        user = cls.get_by_student_id(student_id)
        if not user:
            return False
    
        user.set_password(new_password)
        db.session.commit()
        return True
