"""
权限控制装饰器
提供角色权限、用户状态检查、防重复提交等功能
"""

from functools import wraps
from flask import flash, redirect, url_for, session, request
from flask_login import current_user
from app.models.submission import Submission


def role_required(role):
    """
    角色权限装饰器
    限制只有特定角色的用户才能访问

    Args:
        role (str): 允许的角色名称

    Returns:
        function: 装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            if current_user.role != role:
                flash('权限不足，无法访问此页面', 'danger')
                return redirect(url_for('questionnaire.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def roles_allowed(roles):
    """
    多角色权限装饰器
    允许指定角色列表中的任意一个访问

    Args:
        roles (list): 允许的角色名称列表

    Returns:
        function: 装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            if current_user.role not in roles:
                flash('权限不足，无法访问此页面', 'danger')
                return redirect(url_for('questionnaire.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_user_disabled(f):
    """
    检查用户是否被禁用的装饰器
    如果用户被禁用则自动登出
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        if current_user.is_disabled():
            from flask_login import logout_user
            logout_user()
            flash('您的账户已被禁用，请联系管理员', 'danger')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function


def prevent_duplicate_submission(hours=24):
    """
    防止重复提交的装饰器
    限制用户在指定时间内只能提交一次

    Args:
        hours (int): 时间间隔（小时），默认 24 小时

    Returns:
        function: 装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            # 检查是否有最近的提交记录
            if Submission.has_recent_submission(current_user.id, hours):
                flash(f'您在 {hours}小时内已经提交过问卷，不能重复提交', 'warning')
                return redirect(url_for('report.view'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_submission_ownership(f):
    """
    验证提交数据所有权的装饰器
    确保用户只能访问自己的提交记录

    Args:
        f: 视图函数

    Returns:
        function: 装饰器函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        # 如果不是管理员，检查数据所有权
        if current_user.role != 'admin':
            submission_id = kwargs.get(
                'submission_id') or request.args.get('id')
            if submission_id:
                from app.models.submission import Submission
                submission = Submission.query.get(int(submission_id))
                if submission and submission.user_id != current_user.id:
                    flash('无权访问他人的数据', 'danger')
                    return redirect(url_for('questionnaire.index'))

        return f(*args, **kwargs)
    return decorated_function
