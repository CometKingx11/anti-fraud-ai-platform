"""
认证视图控制器
处理用户登录、登出等认证相关请求
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.utils.helpers import validate_student_id
from app.services.audit_service import AuditService

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
                # 记录安全事件：尝试登录被禁用的账户
                AuditService.log_security_event(
                    'ACCOUNT_LOCKOUT',
                    f'被禁用的账户尝试登录：{user.student_id}',
                    severity='medium',
                    user=user
                )
                flash('您的账户已被禁用，请联系管理员', 'danger')
                return render_template('auth/login.html')

            # 验证密码
            if user.check_password(password):
                # 登录成功
                login_user(user, remember=remember)

                # 更新最后登录时间
                user.update_last_login()
                
                # 记录操作日志：登录成功
                AuditService.log_user_action(
                    user=user,
                    action_type='LOGIN',
                    description=f'{user.name} 登录系统',
                    status='success'
                )

                # 清除可能的警告信息
                session.pop('_flashes', None)

                next_page = request.args.get('next')
                flash('登录成功', 'success')
                
                # 根据角色跳转到对应首页
                if user.role == 'admin':
                    # 管理员如果有 next 参数且指向问卷页面，则跳转过去
                    if next_page and 'questionnaire' in next_page:
                        return redirect(next_page)
                    # 否则默认跳转到仪表板
                    return redirect(url_for('admin.dashboard'))
                elif user.role == 'teacher':
                    # 教师跳转到问卷首页
                    return redirect(url_for('questionnaire.index'))
                else:
                    # 学生用户
                    if next_page:
                        return redirect(next_page)
                    # 否则跳转到问卷首页
                    return redirect(url_for('questionnaire.index'))
            else:
                # 密码错误，记录失败日志和安全事件
                if user:
                    # 记录操作日志：登录失败
                    AuditService.log_user_action(
                        user=user,
                        action_type='LOGIN',
                        description=f'{user.name} 登录失败 - 密码错误',
                        status='failed',
                        error_message='密码错误'
                    )
                    
                    # 记录安全事件：可疑登录尝试
                    from app import db
                    failed_count = db.session.query(User).filter(
                        User.student_id == student_id
                    ).count()  # TODO: 应该实现失败次数统计
                    
                    if failed_count >= 5:  # 简单示例，实际应该用缓存或计数器
                        AuditService.log_security_event(
                            'BRUTE_FORCE',
                            f'多次登录失败：{student_id}，可能存在暴力破解',
                            severity='high',
                            user=user
                        )
                
                flash('学号或密码错误', 'danger')
        else:
            # 用户不存在，记录可疑事件
            AuditService.log_security_event(
                'SUSPICIOUS_LOGIN',
                f'不存在的学号尝试登录：{student_id}',
                severity='low'
            )
            flash('学号或密码错误', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户自助注册（仅对学生开放）
    """
    if current_user.is_authenticated:
        return redirect(url_for('questionnaire.index'))

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # 验证学号格式
        if not validate_student_id(student_id):
            flash('学号格式不正确（应为 8-12 位数字）', 'danger')
            return render_template('auth/register.html')

        # 检查学号是否已存在
        existing_user = User.get_by_student_id(student_id)
        if existing_user:
            flash('该学号已被注册，请直接登录或使用其他学号', 'danger')
            return render_template('auth/register.html')

        # 验证姓名
        if not name:
            flash('请输入姓名', 'danger')
            return render_template('auth/register.html')

        # 验证密码
        if len(password) < 6:
            flash('密码长度至少为 6 位', 'danger')
            return render_template('auth/register.html')

        # 验证两次密码输入一致
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return render_template('auth/register.html')

        try:
            # 创建用户（默认为学生角色）
            user = User.create_user(
                student_id=student_id,
                password=password,
                role='student',
                name=name
            )
            
            # 发送欢迎邮件（如果提供了邮箱）
            if email:
                try:
                    from app.services.email_service import EmailService
                    EmailService.send_welcome_email(email, name, student_id)
                    flash(f'注册成功！欢迎邮件已发送至 {email}', 'success')
                except Exception as e:
                    current_app.logger.error(f'发送欢迎邮件失败：{str(e)}')
                    flash(f'注册成功！邮件发送失败：{str(e)}', 'warning')
            else:
                flash(f'注册成功！请使用学号 {student_id} 登录', 'success')
            
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'注册失败：{str(e)}', 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    用户登出
    """
    from flask_login import logout_user
    
    # 记录操作日志：登出
    AuditService.log_user_action(
        user=current_user,
        action_type='LOGOUT',
        description=f'{current_user.name} 退出登录',
        status='success'
    )
    
    logout_user()

    # 清理 session 中的敏感数据
    session.pop('assessment', None)
    session.pop('_flashes', None)

    flash('已退出登录', 'info')
    return redirect(url_for('auth.login'))
