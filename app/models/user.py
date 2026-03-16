# Author: 小土豆233
# Date: 2026-03-16 23:42:18
# LastEditTime: 2026-03-16 23:42:27
# LastEditors: 小土豆233
# Description: 用户数据模型，定义了系统中的用户实体
# FilePath: flask_anti_project\app\models\user.py
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
            name (str): 用户姓名，默认为None

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
