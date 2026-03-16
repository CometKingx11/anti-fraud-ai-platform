# Author: 小土豆233
# Date: 2026-03-17 00:11:26
# LastEditTime: 2026-03-17 00:16:37
# LastEditors: 小土豆233
# Description: 管理员视图控制器，处理管理员相关的请求
# FilePath: flask_anti_project\app\views\admin_views.py

from app import db
from app.models.submission import Submission
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
def dashboard():
    """
    管理员仪表板
    显示所有用户的提交记录
    """
    if current_user.role != 'admin':
        flash('权限不足', 'danger')
        return redirect(url_for('questionnaire.index'))

    # 获取所有提交记录，按时间倒序排列
    submissions = Submission.query.order_by(
        Submission.submitted_at.desc()).all()

    return render_template('admin/dashboard.html', submissions=submissions)
