# Author: 脆心柚
# Description: 提交数据模型，存储用户的问卷提交记录

import hashlib
import json
from datetime import datetime
from app import db


class Submission(db.Model):
    """
    提交记录模型
    存储用户问卷提交的数据
    """
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False, index=True)
    base_score = db.Column(db.Integer)
    final_score = db.Column(db.Integer)
    risk_level = db.Column(db.String(20))
    cognitive = db.Column(db.Integer)  # 认知维度得分
    behavior = db.Column(db.Integer)   # 行为维度得分
    experience = db.Column(db.Integer)  # 经历维度得分
    open_text = db.Column(db.Text)
    risk_points = db.Column(db.Text)    # JSON 格式存储风险点列表
    analysis = db.Column(db.Text)       # AI 分析结果
    suggestions = db.Column(db.Text)    # 建议列表 (JSON 格式)
    push_contents = db.Column(db.Text)  # 推送内容列表 (JSON 格式)
    uploaded_images = db.Column(db.Text)  # 上传图片路径列表 (JSON 格式)
    url_risk_info = db.Column(db.Text)  # URL 风险信息列表 (JSON 格式)
    url_risk_score = db.Column(db.Integer, default=0)  # URL 风险加分
    ip_address = db.Column(db.String(50), nullable=True)  # 提交 IP 地址
    submission_hash = db.Column(
        db.String(64), nullable=True, index=True)  # 数据完整性校验
    is_valid = db.Column(db.Boolean, default=True, nullable=False)  # 标记数据是否有效
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联用户
    user = db.relationship(
        'User', backref=db.backref('submissions', lazy=True))

    def to_dict(self):
        """
        将对象转换为字典

        Returns:
            dict: 包含对象数据的字典
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'student_id': self.user.student_id if self.user else None,
            'base_score': self.base_score,
            'final_score': self.final_score,
            'risk_level': self.risk_level,
            'cognitive': self.cognitive,
            'behavior': self.behavior,
            'experience': self.experience,
            'open_text': self.open_text,
            'risk_points': self.parse_json_field(self.risk_points),
            'analysis': self.analysis,
            'suggestions': self.parse_json_field(self.suggestions),
            'push_contents': self.parse_json_field(self.push_contents),
            'uploaded_images': self.parse_json_field(self.uploaded_images),
            'url_risk_info': self.parse_json_field(self.url_risk_info),
            'url_risk_score': self.url_risk_score,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

    @staticmethod
    def parse_json_field(json_str):
        """
        解析 JSON 字段

        Args:
            json_str (str): JSON 字符串

        Returns:
            list: 解析后的列表，如果解析失败则返回空列表
        """
        if not json_str:
            return []

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return []

    @staticmethod
    def generate_submission_hash(data):
        """
        生成提交数据的哈希值用于防篡改验证

        Args:
            data (dict): 提交数据字典

        Returns:
            str: SHA256 哈希值
        """
        # 提取关键字段生成哈希
        hash_data = {
            'user_id': data.get('user_id'),
            'base_score': data.get('base_score'),
            'final_score': data.get('final_score'),
            'risk_level': data.get('risk_level'),
            'submitted_at': data.get('submitted_at', datetime.utcnow().isoformat())
        }
        data_str = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def verify_integrity(self):
        """
        验证数据完整性

        Returns:
            bool: 如果数据未被篡改返回 True，否则返回 False
        """
        if not self.submission_hash:
            return False

        current_data = {
            'user_id': self.user_id,
            'base_score': self.base_score,
            'final_score': self.final_score,
            'risk_level': self.risk_level,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }
        current_hash = self.generate_submission_hash(current_data)
        return current_hash == self.submission_hash

    @staticmethod
    def save_from_dict(data):
        """
        从字典保存提交记录

        Args:
            data (dict): 提交数据字典

        Returns:
            Submission: 保存后的提交对象
        """
        # 将列表转换为 JSON 字符串
        json_fields = ['risk_points', 'suggestions',
                       'push_contents', 'uploaded_images', 'url_risk_info']
        for field in json_fields:
            if field in data and isinstance(data[field], list):
                data[field] = json.dumps(data[field], ensure_ascii=False)

        # 生成数据完整性哈希
        data['submission_hash'] = Submission.generate_submission_hash(data)

        submission = Submission(**data)
        db.session.add(submission)
        db.session.commit()
        return submission

    @classmethod
    def has_recent_submission(cls, user_id, hours=24):
        """
        检查用户最近是否有提交记录（用于防止重复提交）

        Args:
            user_id (int): 用户 ID
            hours (int): 时间间隔（小时），默认 24 小时

        Returns:
            bool: 如果最近有提交返回 True，否则返回 False
        """
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent = cls.query.filter(
            cls.user_id == user_id,
            cls.submitted_at >= cutoff_time
        ).first()
        return recent is not None
