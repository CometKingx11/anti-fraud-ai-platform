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

        if user:
            # 检查用户是否被禁用
            if user.is_disabled():
                flash('您的账户已被禁用，请联系管理员', 'danger')
                return render_template('auth/login.html')

            # 验证密码
            if user.check_password(password):
                # 登录成功
                login_user(user, remember=remember)

                # 更新最后登录时间
                user.update_last_login()

                # 清除可能的警告信息
                session.pop('_flashes', None)

                next_page = request.args.get('next')
                flash('登录成功', 'success')
                
                # 根据角色跳转到对应首页
                if user.role == 'admin':
                    # 管理员始终跳转到仪表板，忽略 next 参数
                    return redirect(url_for('admin.dashboard'))
                elif user.role == 'teacher':
                    # 教师跳转到问卷首页
                    return redirect(url_for('questionnaire.index'))
                else:
                    # 如果有指定的下一页且是学生用户，则跳转过去
                    if next_page:
                        return redirect(next_page)
                    # 否则跳转到问卷首页
                    return redirect(url_for('questionnaire.index'))
            else:
                flash('学号或密码错误', 'danger')
        else:
            flash('学号或密码错误', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    用户登出
    """
    from flask_login import logout_user
    logout_user()

    # 清理 session 中的敏感数据
    session.pop('assessment', None)
    session.pop('_flashes', None)

    flash('已退出登录', 'info')
    return redirect(url_for('auth.login'))
