"""
视图包初始化文件
导入所有蓝图以便统一访问
"""

from app.views.auth_views import auth_bp
from app.views.questionnaire_views import questionnaire_bp
from app.views.report_views import report_bp
from app.views.admin_views import admin_bp
from app.views.questionnaire_mgmt_views import questionnaire_mgmt_bp

__all__ = ['auth_bp', 'questionnaire_bp', 'report_bp', 'admin_bp', 'questionnaire_mgmt_bp']
