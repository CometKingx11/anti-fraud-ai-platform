"""
评分规则版本模型
用于记录评分规则的变更历史，支持版本回滚
"""

from app import db
from datetime import datetime
import json


class ScoringRuleVersion(db.Model):
    """评分规则版本表"""
    
    __tablename__ = 'scoring_rule_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    version_number = db.Column(db.String(20), unique=True, nullable=False)  # 版本号，如 v1.0.0
    version_name = db.Column(db.String(100))  # 版本名称
    
    # 规则数据（JSON 格式）
    rules_data = db.Column(db.Text, nullable=False)  # 完整的规则配置
    
    # 变更说明
    change_description = db.Column(db.Text)  # 变更说明
    changed_by = db.Column(db.String(50))  # 修改人
    
    # 版本状态
    is_current = db.Column(db.Boolean, default=False)  # 是否为当前版本
    is_archived = db.Column(db.Boolean, default=False)  # 是否已归档
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ScoringRuleVersion {self.version_number}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'version_number': self.version_number,
            'version_name': self.version_name,
            'change_description': self.change_description,
            'changed_by': self.changed_by,
            'is_current': self.is_current,
            'is_archived': self.is_archived,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'rules_data': json.loads(self.rules_data) if self.rules_data else {}
        }
    
    @classmethod
    def create_version(cls, version_number, version_name, rules_data, change_description, changed_by):
        """
        创建新版本
        
        Args:
            version_number: 版本号
            version_name: 版本名称
            rules_data: 规则数据（字典）
            change_description: 变更说明
            changed_by: 修改人
            
        Returns:
            新版本对象
        """
        # 将旧版本标记为非当前版本
        db.session.query(cls).filter_by(is_current=True).update({'is_current': False})
        
        # 创建新版本
        version = cls(
            version_number=version_number,
            version_name=version_name,
            rules_data=json.dumps(rules_data, ensure_ascii=False),
            change_description=change_description,
            changed_by=changed_by,
            is_current=True
        )
        
        db.session.add(version)
        db.session.commit()
        
        return version
    
    @classmethod
    def get_current_version(cls):
        """获取当前版本"""
        return cls.query.filter_by(is_current=True).first()
    
    @classmethod
    def get_version_by_number(cls, version_number):
        """根据版本号获取版本"""
        return cls.query.filter_by(version_number=version_number).first()
    
    @classmethod
    def rollback_to_version(cls, version_id, changed_by):
        """
        回滚到指定版本
        
        Args:
            version_id: 版本 ID
            changed_by: 修改人
            
        Returns:
            bool: 是否成功
        """
        version = cls.query.get(version_id)
        if not version:
            return False
        
        # 获取该版本的规则数据
        rules_data = json.loads(version.rules_data)
        
        # 创建新版本（回滚版本）
        new_version_number = f"rollback-{version.version_number}"
        cls.create_version(
            version_number=new_version_number,
            version_name=f"回滚到 {version.version_name}",
            rules_data=rules_data,
            change_description=f"回滚到版本 {version.version_number}",
            changed_by=changed_by
        )
        
        return True
    
    @classmethod
    def get_all_versions(cls, limit=50):
        """获取所有版本（按时间倒序）"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
