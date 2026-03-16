"""
认证视图控制器
处理用户登录、登出等认证相关请求
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.utils.helpers import validate_student_id

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录
    """
    if current_user.is_authenticated:
        return redirect(url_for('questionnaire.index'))

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        # 验证学号格式
        if not validate_student_id(student_id):
            flash('学号格式不正确', 'warning')
            return render_template('auth/login.html')

        # 查找用户
        user = User.get_by_student_id(student_id)

        if user and user.check_password(password):
            # 登录成功
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('登录成功', 'success')
            return redirect(next_page) if next_page else redirect(url_for('questionnaire.index'))
        else:
            flash('学号或密码错误', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    用户登出
    """
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('auth.login'))
