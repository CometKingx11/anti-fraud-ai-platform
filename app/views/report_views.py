# Author: 小土豆 233
# Description: 报告视图控制器，处理评估报告相关的请求

from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, send_file
from flask_login import login_required, current_user
from app.services.pdf_service import PDFService
from app.utils.decorators import validate_submission_ownership
import json

# 创建报告蓝图
report_bp = Blueprint('report', __name__, url_prefix='/report')


@report_bp.route('/api/chart-data')
@login_required
def chart_data():
    """
    ECharts 图表数据 API
    返回可视化所需的原始数据
    """
    if 'assessment' not in session:
        from app.models.submission import Submission
        recent_submission = Submission.query.filter_by(
            user_id=current_user.id
        ).order_by(Submission.submitted_at.desc()).first()
        
        if recent_submission:
            assessment_data = recent_submission.to_dict()
        else:
            return json.dumps({'error': '无评估数据'}), 404
    else:
        assessment_data = session['assessment'].copy()
    
    # 准备图表数据
    # 注意：assessment_data 中的 JSON 字段可能已经是字符串格式，不需要再次转换
    chart_data = {
        'scores': {
            'cognitive': assessment_data.get('cognitive', 0) or 0,
            'behavior': assessment_data.get('behavior', 0) or 0,
            'experience': assessment_data.get('experience', 0) or 0
        },
        'base_score': assessment_data.get('base_score', 0) or 0,
        'url_risk_score': assessment_data.get('url_risk_score', 0) or 0,
        'final_score': assessment_data.get('final_score', 0) or 0,
        'risk_level': assessment_data.get('risk_level', '未知'),
        'risk_points': assessment_data.get('risk_points', []),
        'url_risk_info': assessment_data.get('url_risk_info', [])
    }
    
    return json.dumps(chart_data, ensure_ascii=False)


@report_bp.route('/')
@login_required
@validate_submission_ownership
def view():
    """
    查看评估报告
    显示用户的评估结果
    """
    if 'assessment' not in session:
        # 尝试从数据库加载最近的提交记录
        from app.models.submission import Submission
        recent_submission = Submission.query.filter_by(
            user_id=current_user.id
        ).order_by(Submission.submitted_at.desc()).first()

        if recent_submission:
            # 验证数据完整性
            if not recent_submission.verify_integrity():
                flash('警告：该报告数据可能已被篡改', 'danger')

            # 将数据库记录转换为 session 格式
            assessment_data = recent_submission.to_dict()
            session['assessment'] = assessment_data
        else:
            flash('无评估数据，请先填写问卷', 'warning')
            return redirect(url_for('questionnaire.index'))

    # 解析 JSON 数据
    assessment_data = session['assessment'].copy()
    json_fields = ['risk_points', 'suggestions', 'push_contents']
    for field in json_fields:
        if field in assessment_data and isinstance(assessment_data[field], str):
            try:
                assessment_data[field] = json.loads(assessment_data[field])
            except json.JSONDecodeError:
                assessment_data[field] = []
    
    # 【新增】获取 AI 智能分析配置状态
    from app.models.questionnaire import QuestionnaireConfig
    enable_ai_analysis = QuestionnaireConfig.get_config('enable_ai_analysis', '1') == '1'

    return render_template('reports/report.html', data=assessment_data, enable_ai_analysis=enable_ai_analysis)


@report_bp.route('/export-pdf')
@login_required
def export_pdf():
    """
    导出PDF报告
    生成并下载PDF格式的评估报告
    """
    if 'assessment' not in session:
        flash('无评估数据，无法导出PDF', 'warning')
        return redirect(url_for('questionnaire.index'))

    # 获取评估数据
    assessment_data = session['assessment'].copy()

    # 解析 JSON 字段
    json_fields = ['risk_points', 'suggestions', 'push_contents']
    for field in json_fields:
        if field in assessment_data and isinstance(assessment_data[field], str):
            try:
                assessment_data[field] = json.loads(assessment_data[field])
            except json.JSONDecodeError:
                assessment_data[field] = []
        
    # 添加用户信息
    from datetime import datetime
    assessment_data['student_id'] = current_user.student_id
    assessment_data['name'] = current_user.name
    assessment_data['submitted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 生成 PDF
    pdf_buffer = PDFService.generate_report_pdf(assessment_data)

    # 返回PDF文件
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"反诈风险报告_{current_user.student_id}.pdf",
        mimetype='application/pdf'
    )
