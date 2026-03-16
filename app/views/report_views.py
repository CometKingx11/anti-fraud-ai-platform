'''
Author: 小土豆233
Date: 2026-03-17 00:11:19
LastEditTime: 2026-03-17 00:15:13
LastEditors: 小土豆233
Description: 报告视图控制器, 处理评估报告相关的请求
FilePath: \flask_anti_project\app\views\report_views.py
'''

from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, send_file
from flask_login import login_required, current_user
from app.services.pdf_service import PDFService
import json

# 创建报告蓝图
report_bp = Blueprint('report', __name__, url_prefix='/report')


@report_bp.route('/')
@login_required
def view():
    """
    查看评估报告
    显示用户的评估结果
    """
    if 'assessment' not in session:
        flash('无评估数据，请先填写问卷', 'warning')
        return redirect(url_for('questionnaire.index'))

    # 解析JSON数据
    assessment_data = session['assessment'].copy()
    json_fields = ['risk_points', 'suggestions', 'push_contents']
    for field in json_fields:
        if field in assessment_data and isinstance(assessment_data[field], str):
            try:
                assessment_data[field] = json.loads(assessment_data[field])
            except json.JSONDecodeError:
                assessment_data[field] = []

    return render_template('reports/report.html', data=assessment_data)


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

    # 解析JSON字段
    json_fields = ['risk_points', 'suggestions', 'push_contents']
    for field in json_fields:
        if field in assessment_data and isinstance(assessment_data[field], str):
            try:
                assessment_data[field] = json.loads(assessment_data[field])
            except json.JSONDecodeError:
                assessment_data[field] = []

    # 生成PDF
    pdf_buffer = PDFService.generate_report_pdf(assessment_data)

    # 返回PDF文件
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"反诈风险报告_{current_user.student_id}.pdf",
        mimetype='application/pdf'
    )
