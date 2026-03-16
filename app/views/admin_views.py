'''
Author: 小土豆233
Date: 2026-03-17 00:11:26
LastEditTime: 2026-03-17 00:11:46
LastEditors: 小土豆233
Description: 
FilePath: \flask_anti_project\app\views\admin_views.py
'''
"""
认证视图控制器
处理用户登录、登出等认证相关功能
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import login_manager, db

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def load_user(user_id):
    """
    加载用户回调函数
    Flask-Login使用此函数根据用户ID加载用户对象

    Args:
        user_id (str): 用户ID字符串

    Returns:
        User: 用户对象
    """
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录视图
    处理用户登录请求，支持自动创建学生账号
    """
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        password = request.form.get('password', '123456')  # 测试模式默认密码

        # 查找用户
        user = User.get_by_student_id(student_id)

        # 如果用户不存在且为学生，自动创建账号
        if not user and student_id != 'admin':
            user = User.create_user(
                student_id=student_id,
                password='123456',
                role='student',
                name=f'学生{student_id}'
            )
            flash(f'新账号已创建（学号：{student_id}，密码：123456）', 'info')

        # 验证用户凭据
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            session['role'] = user.role
            flash('登录成功！', 'success')

            # 根据角色重定向
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('questionnaire.index'))
        else:
            flash('学号或密码错误', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    用户登出视图
    清除用户会话并重定向到登录页面
    """
    logout_user()
    session.clear()
    flash('已安全退出', 'info')
    return redirect(url_for('auth.login'))
