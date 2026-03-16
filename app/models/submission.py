'''
Author: 小土豆233
Date: 2026-03-16 23:42:18
LastEditTime: 2026-03-16 23:42:27
LastEditors: 小土豆233
Description: 提交数据模型, 存储用户的问卷提交记录
FilePath: \flask_anti_project\app\__init__.py
'''

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
    risk_points = db.Column(db.Text)    # JSON格式存储风险点列表
    analysis = db.Column(db.Text)       # AI分析结果
    suggestions = db.Column(db.Text)    # 建议列表(JSON格式)
    push_contents = db.Column(db.Text)  # 推送内容列表(JSON格式)
    uploaded_images = db.Column(db.Text)  # 上传图片路径列表(JSON格式)
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
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

    @staticmethod
    def parse_json_field(json_str):
        """
        解析JSON字段

        Args:
            json_str (str): JSON字符串

        Returns:
            list: 解析后的列表，如果解析失败则返回空列表
        """
        if not json_str:
            return []

        import json
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return []

    @staticmethod
    def save_from_dict(data):
        """
        从字典保存提交记录

        Args:
            data (dict): 提交数据字典

        Returns:
            Submission: 保存后的提交对象
        """
        # 将列表转换为JSON字符串
        json_fields = ['risk_points', 'suggestions',
                       'push_contents', 'uploaded_images']
        for field in json_fields:
            if field in data and isinstance(data[field], list):
                import json
                data[field] = json.dumps(data[field], ensure_ascii=False)

        submission = Submission(**data)
        db.session.add(submission)
        db.session.commit()
        return submission
