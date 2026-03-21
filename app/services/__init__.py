"""
服务包初始化文件
导入所有服务类以便统一访问
"""

from app.services.assessment_service import AssessmentService
from app.services.ai_analysis_service import AIAnalysisService
from app.services.pdf_service import PDFService
from app.services.audit_service import AuditService

__all__ = ['AssessmentService', 'AIAnalysisService', 'PDFService', 'AuditService']
