# Author: 小土豆233
# Date: 2026-03-16 23:50:59
# LastEditTime: 2026-03-17 00:20:14
# LastEditors: 小土豆233
# Description: 模型包初始化文件，导入所有模型类以便统一访问
# FilePath: flask_anti_project\app\models\__init__.py

from app.models.user import User
from app.models.submission import Submission
from app.models.audit_log import AuditLog
from app.models.security_log import SecurityLog
from app.models.scoring_rule_version import ScoringRuleVersion

__all__ = ['User', 'Submission', 'AuditLog', 'SecurityLog', 'ScoringRuleVersion']
