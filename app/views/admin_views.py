# Author: 小土豆 233
# Description: 管理员视图控制器，处理管理员相关的请求

from app import db
from app.models.submission import Submission
from app.models.user import User
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, request
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.services.export_service import ExportService
from sqlalchemy import func

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@role_required('admin')
def dashboard():
    """
    管理员仪表板
    显示所有用户的提交记录（支持筛选、排序、搜索和分页）
    """
    # 获取筛选参数
    risk_filter = request.args.get('risk_level', 'all')  # all, 极高风险，高风险，中风险，低风险
    sort_by = request.args.get('sort', 'submitted_at')  # submitted_at, final_score, submit_count
    order = request.args.get('order', 'desc')  # asc, desc
    
    # 获取搜索参数
    search_keyword = request.args.get('search', '').strip()  # 搜索关键词（学号或姓名）
    
    # 获取时间筛选参数
    date_filter_type = request.args.get('date_filter_type', 'all')  # all, before, after, between
    start_date = request.args.get('start_date', '').strip()  # 开始时间
    end_date = request.args.get('end_date', '').strip()  # 结束时间
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)  # 每页显示条数，默认 20
    
    # 基础查询
    submissions_query = Submission.query.join(User)
    
    # 风险等级筛选
    if risk_filter != 'all':
        submissions_query = submissions_query.filter(Submission.risk_level == risk_filter)
    
    # 搜索筛选（按学号或姓名）
    if search_keyword:
        submissions_query = submissions_query.filter(
            db.or_(
                User.student_id.like(f'%{search_keyword}%'),
                User.name.like(f'%{search_keyword}%')
            )
        )
    
    # 时间筛选
    if date_filter_type != 'all':
        if date_filter_type == 'before' and start_date:  # 使用 start_date 作为“之前”的时间点
            submissions_query = submissions_query.filter(Submission.submitted_at <= start_date)
        elif date_filter_type == 'after' and start_date:  # 使用 start_date 作为“之后”的时间点
            submissions_query = submissions_query.filter(Submission.submitted_at >= start_date)
        elif date_filter_type == 'between':
            if start_date and end_date:
                submissions_query = submissions_query.filter(
                    Submission.submitted_at >= start_date,
                    Submission.submitted_at <= end_date
                )
            elif start_date:
                submissions_query = submissions_query.filter(Submission.submitted_at >= start_date)
            elif end_date:
                submissions_query = submissions_query.filter(Submission.submitted_at <= end_date)
    
    # 排序
    if sort_by == 'final_score':
        if order == 'asc':
            submissions_query = submissions_query.order_by(Submission.final_score.asc())
        else:
            submissions_query = submissions_query.order_by(Submission.final_score.desc())
    elif sort_by == 'submit_count':
        # 按提交次数排序需要子查询
        subq = db.session.query(
            Submission.user_id,
            func.count(Submission.id).label('cnt')
        ).group_by(Submission.user_id).subquery()
        
        if order == 'asc':
            submissions_query = submissions_query.outerjoin(subq, Submission.user_id == subq.c.user_id).order_by(subq.c.cnt.asc())
        else:
            submissions_query = submissions_query.outerjoin(subq, Submission.user_id == subq.c.user_id).order_by(subq.c.cnt.desc())
    else:  # submitted_at
        if order == 'asc':
            submissions_query = submissions_query.order_by(Submission.submitted_at.asc())
        else:
            submissions_query = submissions_query.order_by(Submission.submitted_at.desc())
    
    # 分页
    pagination = submissions_query.paginate(page=page, per_page=per_page, error_out=False)
    all_submissions = pagination.items
    
    # 统计每个用户的提交次数
    submission_counts = db.session.query(
        Submission.user_id,
        func.count(Submission.id).label('count')
    ).group_by(Submission.user_id).all()
    count_dict = {sc.user_id: sc.count for sc in submission_counts}
    
    # 为每个提交对象添加提交次数属性
    for s in all_submissions:
        s.submit_count = count_dict.get(s.user_id, 0)
    
    # 获取高风险用户 TOP10（按平均风险分排序）
    high_risk_users = db.session.query(
        User.id,
        User.student_id,
        User.name,
        func.avg(Submission.final_score).label('avg_score'),
        func.count(Submission.id).label('total_submits'),
        func.max(Submission.risk_level).label('max_risk')
    ).join(Submission).filter(
        Submission.risk_level.in_(['高风险', '极高风险'])
    ).group_by(User.id).order_by(
        func.avg(Submission.final_score).desc()
    ).limit(10).all()
    
    # 统计数据
    total_submissions = Submission.query.count()
    total_students = User.query.filter_by(role='student').count()
    high_risk_count = Submission.query.filter(Submission.risk_level.in_(['高风险', '极高风险'])).count()
    
    # 未处理安全事件数量
    from app.models.security_log import SecurityLog
    unhandled_security_events = SecurityLog.query.filter_by(is_handled=False).count()
    
    # 导入时区转换工具
    from datetime import timedelta
    from flask import current_app
    
    return render_template('admin/dashboard.html', 
                         submissions=all_submissions,
                         pagination=pagination,
                         total_submissions=total_submissions,
                         total_students=total_students,
                         high_risk_count=high_risk_count,
                         unhandled_security_events=unhandled_security_events,
                         high_risk_users=high_risk_users,
                         config=current_app.config,
                         timedelta=timedelta,
                         current_risk=risk_filter,
                         current_sort=sort_by,
                         current_order=order,
                         search_keyword=search_keyword,
                         per_page=per_page,
                         date_filter_type=date_filter_type,
                         start_date=start_date,
                         end_date=end_date)


@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    """
    用户管理页面
    显示所有用户列表（支持按角色分页）
    """
    # 获取当前页码
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', 'all')  # all, student, teacher, admin
    risk_filter = request.args.get('risk', '')  # 极高风险，高风险，中风险，低风险
    search_keyword = request.args.get('search', '').strip()  # 搜索关键词
    per_page = request.args.get('per_page', 20, type=int)  # 每页显示条数，默认 20
    
    # 根据角色筛选
    if role_filter == 'all':
        users_query = User.query.order_by(User.role, User.student_id)
    else:
        users_query = User.query.filter_by(role=role_filter).order_by(User.student_id)
    
    # 如果有风险等级筛选，筛选所有角色
    if risk_filter and risk_filter != 'all' and role_filter in ['student', 'teacher', 'admin']:
        # 通过提交记录关联筛选有风险等级的用户
        user_ids_with_risk = db.session.query(
            Submission.user_id
        ).join(User).filter(
            User.role == role_filter,
            Submission.risk_level == risk_filter
        ).distinct().subquery()
        
        users_query = users_query.filter(User.id.in_(user_ids_with_risk))
    
    # 如果有搜索关键词，进行筛选
    if search_keyword:
        # 按学号或姓名搜索
        users_query = users_query.filter(
            db.or_(
                User.student_id.like(f'%{search_keyword}%'),
                User.name.like(f'%{search_keyword}%')
            )
        )
    
    # 分页（支持动态每页条数）
    pagination = users_query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    # 统计各角色数量
    total_students = User.query.filter_by(role='student').count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_admins = User.query.filter_by(role='admin').count()
    
    return render_template('admin/users.html', 
                         users=users, 
                         pagination=pagination,
                         current_role=role_filter,
                         search_keyword=search_keyword,
                         per_page=per_page,  # 传递给模板
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_admins=total_admins)


@admin_bp.route('/users/<int:user_id>')
@login_required
@role_required('admin')
def view_user(user_id):
    """
    查看用户详情
    """
    user = User.query.get_or_404(user_id)
    
    # 获取该用户的所有提交记录
    submissions = Submission.query.filter_by(
        user_id=user_id
    ).order_by(Submission.submitted_at.desc()).all()
    
    return render_template('admin/user_detail.html', user=user, submissions=submissions)


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
        # 兼容 password 和 new_password 字段
        new_password = request.form.get('new_password', '') or request.form.get('password', '')
        new_password = new_password.strip() if new_password else ''

        try:
            # 准备更新数据
            update_data = {
                'name': name,
                'email': email,
                'role': role,
                'is_active': is_active
            }

            # 如果要重置密码（编辑模式下使用 new_password 字段）
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
        # 先删除该用户的所有提交记录（避免外键约束错误）
        submissions = Submission.query.filter_by(user_id=user_id).all()
        for submission in submissions:
            db.session.delete(submission)
        
        # 删除用户
        deleted_name = user.name
        deleted_student_id = user.student_id
        User.delete_user(user_id)
        
        # 记录操作日志
        from app.services.audit_service import AuditService
        AuditService.log_user_action(
            user=current_user,
            action_type='DELETE_USER',
            description=f'删除用户：{deleted_name} ({deleted_student_id})',
            status='success',
            target_type='User',
            target_id=user_id
        )
        
        flash(f'用户 {deleted_student_id} 已删除', 'success')
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
        # 设置固定密码
        new_password = '12345678'

        # 重置密码
        User.reset_password(user.student_id, new_password)
        
        # 记录操作日志
        from app.services.audit_service import AuditService
        AuditService.log_user_action(
            user=current_user,
            action_type='RESET_PASSWORD',
            description=f'重置用户密码：{user.name} ({user.student_id})',
            status='success',
            target_type='User',
            target_id=user.id
        )

        flash(f'用户 {user.student_id} 密码已重置为：{new_password}', 'info')
    except Exception as e:
        flash(f'重置失败：{str(e)}', 'danger')

    return redirect(url_for('admin.users'))


@admin_bp.route('/users/batch-delete', methods=['POST'])
@login_required
@role_required('admin')
def batch_delete_users():
    """
    批量删除用户
    """
    user_ids = request.form.getlist('user_ids')
    
    if not user_ids:
        flash('未选择要删除的用户', 'warning')
        return redirect(url_for('admin.users'))
    
    success_count = 0
    failed_count = 0
    errors = []
    
    for user_id_str in user_ids:
        try:
            user_id = int(user_id_str)
            user = User.query.get_or_404(user_id)
            
            # 不能删除自己
            if user.id == current_user.id:
                failed_count += 1
                errors.append(f'不能删除当前登录的管理员账户：{user.student_id}')
                continue
            
            # 不能删除管理员
            if user.role == 'admin':
                failed_count += 1
                errors.append(f'不能删除管理员账户：{user.student_id}')
                continue
            
            # 先删除该用户的所有提交记录（避免外键约束错误）
            submissions = Submission.query.filter_by(user_id=user_id).all()
            for submission in submissions:
                db.session.delete(submission)
            
            # 删除用户
            User.delete_user(user_id)
            success_count += 1
            
        except Exception as e:
            failed_count += 1
            errors.append(f'删除失败 {user_id_str}: {str(e)}')
    
    # 显示结果
    if success_count > 0:
        flash(f'成功删除 {success_count} 个用户', 'success')
    
    if failed_count > 0:
        flash(f'失败 {failed_count} 个用户', 'warning')
        for error in errors[:5]:  # 只显示前 5 个错误
            flash(error, 'danger')
        if len(errors) > 5:
            flash(f'还有 {len(errors) - 5} 个错误未显示', 'warning')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/set-password', methods=['POST'])
@login_required
@role_required('admin')
def set_user_password(user_id):
    """
    为用户设置指定密码
    """
    user = User.query.get_or_404(user_id)

    # 不能设置自己的密码
    if user.id == current_user.id:
        flash('请通过个人中心修改密码', 'warning')
        return redirect(url_for('admin.users'))

    # 获取表单数据
    new_password = request.form.get('set_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()

    # 验证密码
    if not new_password or len(new_password) < 6:
        flash('密码长度至少为 6 位', 'danger')
        return redirect(url_for('admin.view_user', user_id=user.id))

    if new_password != confirm_password:
        flash('两次输入的密码不一致', 'danger')
        return redirect(url_for('admin.view_user', user_id=user.id))

    try:
        # 设置新密码
        User.reset_password(user.student_id, new_password)
        
        # 记录操作日志
        from app.services.audit_service import AuditService
        AuditService.log_user_action(
            user=current_user,
            action_type='SET_PASSWORD',
            description=f'为用户设置密码：{user.name} ({user.student_id})',
            status='success',
            target_type='User',
            target_id=user.id
        )
        
        flash(f'用户 {user.student_id} 密码已设置为：{new_password}', 'success')
    except Exception as e:
        flash(f'设置失败：{str(e)}', 'danger')

    return redirect(url_for('admin.view_user', user_id=user.id))


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

        # 检查文件扩展名（支持 CSV 和 XLSX）
        if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            try:
                from app.services.batch_import_service import import_users_from_file
                import os
                from werkzeug.utils import secure_filename

                # 保存上传的文件
                uploads_dir = os.path.join(os.getcwd(), 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                filename = secure_filename(file.filename)
                file_path = os.path.join(uploads_dir, filename)
                file.save(file_path)

                # 导入用户（自动识别文件类型）
                result = import_users_from_file(file_path)

                # 显示结果
                if result['success'] > 0:
                    flash(f'成功导入 {result["success"]} 个用户', 'success')
                    flash('未设置密码的账户将使用默认密码：12345678', 'info')
                if result['failed'] > 0:
                    flash(f'失败 {result["failed"]} 个用户', 'warning')

                if result['errors']:
                    for error in result['errors'][:5]:  # 只显示前 5 个错误
                        flash(error, 'danger')
                    if len(result['errors']) > 5:
                        flash(f'还有 {len(result["errors"]) - 5} 个错误未显示', 'warning')

                # 尝试删除临时文件（即使失败也不影响导入结果）
                try:
                    import time
                    time.sleep(0.1)  # 等待文件句柄释放
                    os.remove(file_path)
                except Exception as remove_error:
                    # 文件删除失败不影响导入成功，只记录日志
                    import logging
                    logging.warning(f'临时文件删除失败：{file_path}, 错误：{str(remove_error)}')

                return redirect(url_for('admin.users'))

            except Exception as e:
                flash(f'导入失败：{str(e)}', 'danger')
        else:
            flash('只支持 CSV 和 Excel (.xlsx) 格式文件', 'danger')

    return render_template('admin/import_users.html')


@admin_bp.route('/users/download-template')
@login_required
@role_required('admin')
def download_import_template():
    """
    下载导入模板（Excel 格式）
    """
    from flask import send_file
    import os
    
    # 检查是否有 Excel 模板文件
    excel_template_path = os.path.join(os.getcwd(), 'students_for_import.xlsx')
    
    if os.path.exists(excel_template_path):
        return send_file(
            excel_template_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='用户导入模板.xlsx'
        )
    else:
        # 如果 Excel 模板不存在，尝试生成
        try:
            from openpyxl import Workbook
            
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "用户导入"
            
            # 添加表头
            headers = ['student_id', 'name', 'email', 'role', 'password']
            ws.append(headers)
            
            # 添加示例数据
            sample_data = [
                ['20240001', '张三', 'zhangsan@example.com', 'student', '123456'],
                ['20240002', '李四', 'lisi@example.com', 'student', '123456'],
                ['20240003', '王五', 'wangwu@example.com', 'student', '123456'],
                ['20240004', '赵六', 'zhaoliu@example.com', 'teacher', '123456'],
                ['20240005', '钱七', 'qianqi@example.com', 'student', ''],
            ]
            
            for data in sample_data:
                ws.append(data)
            
            # 调整列宽
            ws.column_dimensions['A'].width = 15
            ws.column_dimensions['B'].width = 10
            ws.column_dimensions['C'].width = 25
            ws.column_dimensions['D'].width = 10
            ws.column_dimensions['E'].width = 12
            
            # 保存文件
            os.makedirs(os.path.join(os.getcwd(), 'uploads'), exist_ok=True)
            template_path = os.path.join(os.getcwd(), 'students_for_import.xlsx')
            wb.save(template_path)
            wb.close()
            
            return send_file(
                template_path,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='用户导入模板.xlsx'
            )
            
        except ImportError:
            flash('缺少 openpyxl 库，无法生成 Excel 模板。请安装：pip install openpyxl==3.1.2', 'danger')
            return redirect(url_for('admin.import_users'))
        except Exception as e:
            flash(f'生成模板失败：{str(e)}', 'danger')
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


@admin_bp.route('/submissions/<int:submission_id>/view-report')
@login_required
@role_required('admin')
def view_submission_report(submission_id):
    """
    查看指定提交记录的详细报告
    """
    submission = Submission.query.get_or_404(submission_id)
    
    # 将提交记录转换为字典格式，与评估数据格式保持一致
    report_data = submission.to_dict()
    
    # 解析 JSON 字段
    json_fields = ['risk_points', 'suggestions', 'push_contents', 'uploaded_images', 'url_risk_info']
    for field in json_fields:
        if field in report_data and isinstance(report_data[field], str):
            try:
                import json
                report_data[field] = json.loads(report_data[field])
            except:
                report_data[field] = []
    
    # 确保有 assessment 需要的关键字段
    if 'assessment' not in report_data:
        report_data['assessment'] = report_data
    
    # 导入配置和时区转换
    from datetime import timedelta
    from flask import current_app
    
    return render_template(
        'admin/submission_report.html',
        submission=submission,
        data=report_data,
        config=current_app.config,
        timedelta=timedelta
    )


@admin_bp.route('/submissions/<int:submission_id>/export-pdf')
@login_required
@role_required('admin')
def export_submission_pdf(submission_id):
    """
    导出指定提交记录的 PDF 报告
    """
    from app.services.pdf_service import PDFService
    
    submission = Submission.query.get_or_404(submission_id)
    
    # 将提交记录转换为字典格式
    assessment_data = submission.to_dict()
    
    # 解析 JSON 字段
    json_fields = ['risk_points', 'suggestions', 'push_contents']
    for field in json_fields:
        if field in assessment_data and isinstance(assessment_data[field], str):
            try:
                import json
                assessment_data[field] = json.loads(assessment_data[field])
            except:
                assessment_data[field] = []
    
    # 确保包含用户信息和提交时间
    if submission.user:
        assessment_data['student_id'] = submission.user.student_id
        assessment_data['name'] = submission.user.name
    assessment_data['submitted_at'] = submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
    
    # 生成 PDF
    pdf_buffer = PDFService.generate_report_pdf(assessment_data)
    
    # 返回 PDF 文件
    filename = f"反诈风险评估报告_{submission.user.student_id}_{submission.submitted_at.strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@admin_bp.route('/uploads/<filename>')
@login_required
@role_required('admin')
def uploaded_file(filename):
    """
    提供上传文件的访问
    """
    import os
    from werkzeug.utils import secure_filename
    
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    
    # 直接使用文件名，不使用 secure_filename（因为会破坏中文）
    # 但需要手动清理路径防止遍历攻击
    safe_filename = filename.replace('..', '').replace('/', '').replace('\\\\', '')
    file_path = os.path.join(uploads_dir, safe_filename)
    
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        flash(f'文件不存在：{safe_filename}', 'danger')
        print(f"文件不存在：{file_path}")  # 调试信息
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/submissions/<int:submission_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_submission(submission_id):
    """
    删除指定的提交记录
    """
    submission = Submission.query.get_or_404(submission_id)
    
    try:
        # 删除相关的图片文件
        import os
        import json
        
        if submission.uploaded_images:
            try:
                image_paths = json.loads(submission.uploaded_images)
                for image_path in image_paths:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        print(f"已删除图片：{image_path}")
            except:
                pass  # 如果解析失败，跳过图片删除
        
        # 删除提交记录
        db.session.delete(submission)
        db.session.commit()
        
        flash(f'✅ 成功删除提交记录（ID: {submission_id}）', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ 删除失败：{str(e)}', 'danger')
        print(f"删除提交记录失败：{str(e)}")
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/submissions/delete-multiple', methods=['POST'])
@login_required
@role_required('admin')
def delete_multiple_submissions():
    """
    批量删除提交记录
    """
    # 获取选中的提交 ID 列表
    submission_ids = request.form.getlist('submission_ids[]')
    
    if not submission_ids:
        flash('❌ 请选择要删除的提交记录', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    try:
        deleted_count = 0
        for submission_id in submission_ids:
            submission = Submission.query.get(int(submission_id))
            if submission:
                # 删除相关的图片文件
                import os
                import json
                
                if submission.uploaded_images:
                    try:
                        image_paths = json.loads(submission.uploaded_images)
                        for image_path in image_paths:
                            if os.path.exists(image_path):
                                os.remove(image_path)
                    except:
                        pass
                
                # 删除提交记录
                db.session.delete(submission)
                deleted_count += 1
        
        db.session.commit()
        flash(f'✅ 成功删除 {deleted_count} 条提交记录', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ 批量删除失败：{str(e)}', 'danger')
        print(f"批量删除失败：{str(e)}")
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/ai-report')
@login_required
@role_required('admin')
def ai_report():
    """
    AI 统计报告页面
    显示基于千问 AI 生成的整体统计分析报告
    """
    from app.services.ai_report_service import AIReportService
    
    # 获取筛选参数
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    risk_level = request.args.get('risk_level', 'all')
    generate = request.args.get('generate', '0')  # 是否生成报告的标志
    
    # 如果不是'all'则使用筛选，否则不使用
    risk_filter = risk_level if risk_level != 'all' else None
    
    # 只有当用户点击生成按钮时才生成报告
    report = None
    if generate == '1':
        # 生成报告
        report_service = AIReportService()
        report = report_service.generate_statistical_report(
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None,
            risk_level=risk_filter
        )
    
    # 获取缓存信息
    cache_info = AIReportService.get_cache_info()
    
    return render_template('admin/ai_report.html', 
                         report=report,
                         start_date=start_date,
                         end_date=end_date,
                         risk_level=risk_level,
                         generate=generate == '1',  # 传递给模板是否已生成
                         cache_info=cache_info)


@admin_bp.route('/export-ai-report', methods=['POST'])
@login_required
@role_required('admin')
def export_ai_report():
    """
    导出 AI 统计报告为 PDF 格式
    """
    from app.services.ai_report_service import AIReportService
    from app.services.export_service import ExportService
    
    # 获取筛选参数
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    risk_level = request.form.get('risk_level', 'all')
    
    # 如果不是'all'则使用筛选，否则不使用
    risk_filter = risk_level if risk_level != 'all' else None
    
    try:
        # 生成报告
        report_service = AIReportService()
        report = report_service.generate_statistical_report(
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None,
            risk_level=risk_filter
        )
        
        # 导出为 PDF
        pdf_buffer = ExportService.export_ai_report_to_pdf(report['ai_analysis'])
        
        # 发送文件
        filename = ExportService.get_export_filename('ai_report')
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'❌ 导出失败：{str(e)}', 'danger')
        print(f"导出 AI 报告失败：{str(e)}")
        return redirect(url_for('admin.ai_report'))


@admin_bp.route('/clear-ai-report-cache', methods=['POST'])
@login_required
@role_required('admin')
def clear_ai_report_cache():
    """
    清除 AI 报告缓存
    """
    from app.services.ai_report_service import AIReportService
    
    try:
        AIReportService.clear_cache()
        flash('✅ 已清除 AI 报告缓存，下次生成将使用最新数据', 'success')
    except Exception as e:
        flash(f'❌ 清除缓存失败：{str(e)}', 'danger')
    
    return redirect(url_for('admin.ai_report'))

