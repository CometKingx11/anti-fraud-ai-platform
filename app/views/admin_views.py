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


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_user():
    """
    创建新用户
    """
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')

        # 验证学号格式
        from app.utils.helpers import validate_student_id
        if not validate_student_id(student_id):
            flash('学号格式不正确（应为 8-12 位数字）', 'danger')
            return render_template('admin/user_form.html', action='create')

        # 检查学号是否已存在
        existing_user = User.get_by_student_id(student_id)
        if existing_user:
            flash('该学号已被注册', 'danger')
            return render_template('admin/user_form.html', action='create')

        # 验证密码
        if len(password) < 6:
            flash('密码长度至少为 6 位', 'danger')
            return render_template('admin/user_form.html', action='create')

        try:
            # 创建用户
            User.create_user(
                student_id=student_id,
                password=password,
                role=role,
                name=name
            )
            flash(f'用户 {student_id} 创建成功', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            flash(f'创建失败：{str(e)}', 'danger')

    return render_template('admin/user_form.html', action='create')


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    """
    编辑用户信息
    """
    user = User.query.get_or_404(user_id)

    # 不能编辑自己
    if user.id == current_user.id:
        flash('不能编辑当前登录的管理员账户', 'warning')
        return redirect(url_for('admin.users'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'student')
        is_active = request.form.get('is_active') == 'on'
        new_password = request.form.get('new_password', '')

        try:
            # 准备更新数据
            update_data = {
                'name': name,
                'email': email,
                'role': role,
                'is_active': is_active
            }

            # 如果要重置密码
            if new_password and len(new_password) >= 6:
                update_data['password'] = new_password

            # 更新用户信息
            User.update_user(user_id, **update_data)
            flash(f'用户 {user.student_id} 信息更新成功', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            flash(f'更新失败：{str(e)}', 'danger')

    return render_template('admin/user_form.html', action='edit', user=user)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    """
    删除用户
    """
    user = User.query.get_or_404(user_id)

    # 不能删除自己
    if user.id == current_user.id:
        flash('不能删除当前登录的管理员账户', 'danger')
        return redirect(url_for('admin.users'))

    try:
        # 删除用户
        User.delete_user(user_id)
        flash(f'用户 {user.student_id} 已删除', 'success')
    except Exception as e:
        flash(f'删除失败：{str(e)}', 'danger')

    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@role_required('admin')
def reset_password(user_id):
    """
    重置用户密码
    """
    user = User.query.get_or_404(user_id)

    # 不能重置自己的密码（应该通过其他方式）
    if user.id == current_user.id:
        flash('请通过个人中心修改密码', 'warning')
        return redirect(url_for('admin.users'))

    try:
        # 生成随机密码
        import random
        import string
        new_password = ''.join(random.choices(
            string.ascii_letters + string.digits, k=8))

        # 重置密码
        User.reset_password(user.student_id, new_password)

        flash(f'用户 {user.student_id} 密码已重置为新密码：{new_password}', 'info')
    except Exception as e:
        flash(f'重置失败：{str(e)}', 'danger')

    return redirect(url_for('admin.users'))


@admin_bp.route('/users/import', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def import_users():
    """
    批量导入用户
    """
    if request.method == 'POST':
        # 检查是否有上传文件
        if 'file' not in request.files:
            flash('请选择要上传的文件', 'danger')
            return redirect(url_for('admin.import_users'))

        file = request.files['file']

        if file.filename == '':
            flash('未选择文件', 'danger')
            return redirect(url_for('admin.import_users'))

        if file and file.filename.endswith('.csv'):
            try:
                from app.services.batch_import_service import import_users_from_csv
                import os
                from werkzeug.utils import secure_filename

                # 保存上传的文件
                uploads_dir = os.path.join(os.getcwd(), 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                filename = secure_filename(file.filename)
                file_path = os.path.join(uploads_dir, filename)
                file.save(file_path)

                # 导入用户
                result = import_users_from_csv(file_path)

                # 删除临时文件
                os.remove(file_path)

                # 显示结果
                if result['success'] > 0:
                    flash(f'成功导入 {result["success"]} 个用户', 'success')
                if result['failed'] > 0:
                    flash(f'失败 {result["failed"]} 个用户', 'warning')

                if result['errors']:
                    for error in result['errors'][:5]:  # 只显示前 5 个错误
                        flash(error, 'danger')
                    if len(result['errors']) > 5:
                        flash(f'还有 {len(result["errors"]) - 5} 个错误未显示', 'warning')

                return redirect(url_for('admin.users'))

            except Exception as e:
                flash(f'导入失败：{str(e)}', 'danger')
        else:
            flash('只支持 CSV 格式文件', 'danger')

    return render_template('admin/import_users.html')


@admin_bp.route('/users/download-template')
@login_required
@role_required('admin')
def download_import_template():
    """
    下载导入模板
    """
    from flask import send_file
    import os
    
    template_path = os.path.join(os.getcwd(), 'users_import_example.csv')
    
    if os.path.exists(template_path):
        return send_file(
            template_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name='用户导入模板.csv'
        )
    else:
        flash('模板文件不存在', 'danger')
        return redirect(url_for('admin.import_users'))


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

