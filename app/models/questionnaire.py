"""
问卷题目模型
支持动态配置问卷题目、评分规则
"""

from app import db
from datetime import datetime


class QuestionnaireQuestion(db.Model):
    """问卷题目表"""
    
    __tablename__ = 'questionnaire_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 题目基本信息
    question_number = db.Column(db.Integer, nullable=False, unique=True)  # 题号（1,2,3...）
    category = db.Column(db.String(50), nullable=False)  # 分类：cognitive/behavior/experience/open
    question_text = db.Column(db.Text, nullable=False)  # 题目内容
    
    # 评分规则
    min_score = db.Column(db.Integer, default=1)  # 最小分值
    max_score = db.Column(db.Integer, default=5)  # 最大分值
    
    # 维度权重（用于计算总分）
    dimension = db.Column(db.String(50))  # 所属维度：cognitive/behavior/experience
    weight = db.Column(db.Float, default=1.0)  # 权重系数
    
    # 选项配置（JSON 格式存储选项文本）
    options_json = db.Column(db.Text)  # 例如：{"1":"完全不符合","2":"不太符合",...}
    
    # 状态控制
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    is_required = db.Column(db.Boolean, default=True)  # 是否必答
    
    # 排序
    display_order = db.Column(db.Integer, default=0)  # 显示顺序
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<QuestionnaireQuestion {self.question_number}: {self.question_text[:30]}>'
    
    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'id': self.id,
            'question_number': self.question_number,
            'category': self.category,
            'question_text': self.question_text,
            'min_score': self.min_score,
            'max_score': self.max_score,
            'dimension': self.dimension,
            'weight': self.weight,
            'options': json.loads(self.options_json) if self.options_json else None,
            'is_active': self.is_active,
            'is_required': self.is_required,
            'display_order': self.display_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    @classmethod
    def get_active_questions(cls, category=None):
        """获取所有启用的题目"""
        query = cls.query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        return query.order_by(cls.display_order, cls.question_number).all()
    
    @classmethod
    def calculate_dimension_score(cls, answers: dict, dimension: str) -> int:
        """
        计算某个维度的得分
        
        Args:
            answers: 答案字典 {'q1': 3, 'q2': 5, ...}
            dimension: 维度名称
            
        Returns:
            维度得分
        """
        questions = cls.query.filter_by(
            dimension=dimension,
            is_active=True
        ).all()
        
        total_score = 0
        max_possible = 0
        
        for q in questions:
            answer_key = f'q{q.question_number}'
            if answer_key in answers:
                answer_value = int(answers[answer_key])
                # 根据题目类型计算分数（正向/反向计分）
                if q.category == 'behavior':
                    # 行为风险题：分数越高风险越大（反向计分）
                    score = (q.max_score + q.min_score + 1) - answer_value
                else:
                    # 认知/经历题：分数越高越好（正向计分）
                    score = answer_value
                
                total_score += score * q.weight
                max_possible += q.max_score * q.weight
        
        return round(total_score) if total_score > 0 else 0


class QuestionnaireConfig(db.Model):
    """问卷配置表"""
    
    __tablename__ = 'questionnaire_config'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 配置项
    config_key = db.Column(db.String(100), unique=True, nullable=False)  # 配置键
    config_value = db.Column(db.Text, nullable=False)  # 配置值
    
    # 描述
    description = db.Column(db.Text)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<QuestionnaireConfig {self.config_key}: {self.config_value[:30]}>'
    
    @classmethod
    def get_config(cls, key: str, default=None):
        """获取配置值"""
        config = cls.query.filter_by(config_key=key).first()
        return config.config_value if config else default
    
    @classmethod
    def set_config(cls, key: str, value: str, description: str = ""):
        """设置配置值"""
        config = cls.query.filter_by(config_key=key).first()
        if config:
            config.config_value = value
            config.description = description
        else:
            config = cls(
                config_key=key,
                config_value=value,
                description=description
            )
            db.session.add(config)
        db.session.commit()
        return config
