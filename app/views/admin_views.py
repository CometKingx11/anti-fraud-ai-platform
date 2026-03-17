# Author: 小土豆233
# Date: 2026-03-17 00:11:26
# LastEditTime: 2026-03-17 00:16:37
# LastEditors: 小土豆233
# Description: 管理员视图控制器，处理管理员相关的请求
# FilePath: flask_anti_project\app\views\admin_views.py

from app import db
from app.models.submission import Submission
from app.models.user import User
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, request
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.services.export_service import ExportService

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@role_required('admin')
def dashboard():
    """
    管理员仪表板
    显示所有用户的提交记录
    """
    # 获取所有提交记录，按时间倒序排列
    submissions = Submission.query.order_by(
        Submission.submitted_at.desc()).all()

    return render_template('admin/dashboard.html', submissions=submissions)


@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    """
    用户管理页面
    显示所有用户列表
    """
    # 获取所有用户，按角色和学号排序
    users = User.query.order_by(User.role, User.student_id).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user_status(user_id):
    """
    切换用户状态（禁用/启用）
    """
    user = User.query.get_or_404(user_id)

    # 不能禁用自己
    if user.id == current_user.id:
        flash('不能禁用当前登录的管理员账户', 'warning')
        return redirect(url_for('admin.users'))

    # 切换状态
    user.is_active = not user.is_active
    db.session.commit()

    status_text = '启用' if user.is_active else '禁用'
    flash(f'已成功{status_text}用户 {user.student_id}', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/export')
@login_required
@role_required('admin')
def export():
    """
    导出数据页面
    """
    return render_template('admin/export.html')


@admin_bp.route('/export/csv')
@login_required
@role_required('admin')
def export_csv():
    """
    导出 CSV 格式数据
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    risk_level = request.args.get('risk_level')

    try:
        buffer = ExportService.export_to_csv(
            start_date=start_date,
            end_date=end_date,
            risk_level=risk_level
        )
        filename = ExportService.get_export_filename('csv')
        return send_file(
            buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'导出失败：{str(e)}', 'danger')
        return redirect(url_for('admin.export'))


@admin_bp.route('/export/excel')
@login_required
@role_required('admin')
def export_excel():
    """
    导出 Excel(PDF) 格式数据
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    risk_level = request.args.get('risk_level')

    try:
        buffer = ExportService.export_to_excel(
            start_date=start_date,
            end_date=end_date,
            risk_level=risk_level
        )
        filename = ExportService.get_export_filename('excel')
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'导出失败：{str(e)}', 'danger')
        return redirect(url_for('admin.export'))


@admin_bp.route('/submissions/<int:submission_id>/toggle-valid', methods=['POST'])
@login_required
@role_required('admin')
def toggle_submission_valid(submission_id):
    """
    标记提交记录的有效性
    """
    submission = Submission.query.get_or_404(submission_id)
    submission.is_valid = not submission.is_valid
    db.session.commit()

    status_text = '有效' if submission.is_valid else '无效'
    flash(f'已标记为{status_text}', 'success')
    return redirect(url_for('admin.dashboard'))
