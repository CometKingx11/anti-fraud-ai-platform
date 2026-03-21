"""
日志审计视图
提供日志查看和管理功能
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.services.audit_service import AuditService
from app.utils.decorators import admin_required

audit_bp = Blueprint('audit', __name__, url_prefix='/admin/audit')


@audit_bp.route('/logs')
@login_required
@admin_required
def audit_logs():
    """查看操作日志"""
    # 获取筛选参数
    user_id = request.args.get('user_id', type=int)
    action_type = request.args.get('action_type')
    status = request.args.get('status')
    days = request.args.get('days', default=30, type=int)
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)
    keyword = request.args.get('keyword', '').strip()  # 新增：关键词搜索
    
    # 构建查询
    from app.models.audit_log import AuditLog
    from datetime import datetime, timedelta
    
    query = AuditLog.query
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(AuditLog.created_at >= cutoff_date)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action_type:
        query = query.filter(AuditLog.action_type == action_type)
    
    if status:
        query = query.filter(AuditLog.status == status)
    
    # 关键词搜索（支持描述和 IP 地址）
    if keyword:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                AuditLog.action_description.like(f'%{keyword}%'),
                AuditLog.ip_address.like(f'%{keyword}%')
            )
        )
    
    # 分页
    logs = query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 获取所有用户 ID 用于筛选
    users_query = AuditLog.query.with_entities(
        AuditLog.user_id, AuditLog.user_name
    ).distinct().all()
    
    # 获取所有操作类型
    actions_query = AuditLog.query.with_entities(
        AuditLog.action_type
    ).distinct().all()
    action_types = [a[0] for a in actions_query]
    
    return render_template('admin/audit_logs.html',
                          logs=logs,
                          users=users_query,
                          action_types=action_types,
                          selected_user_id=user_id,
                          selected_action_type=action_type,
                          selected_status=status,
                          selected_days=days)


@audit_bp.route('/security')
@login_required
@admin_required
def security_logs():
    """查看安全日志"""
    # 获取筛选参数
    severity = request.args.get('severity')
    event_type = request.args.get('event_type')
    is_handled = request.args.get('is_handled')
    days = request.args.get('days', default=30, type=int)
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)
    keyword = request.args.get('keyword', '').strip()  # 新增：关键词搜索
    
    from app.models.security_log import SecurityLog
    from datetime import datetime, timedelta
    
    query = SecurityLog.query
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(SecurityLog.created_at >= cutoff_date)
    
    if severity:
        query = query.filter(SecurityLog.severity == severity)
    
    if event_type:
        query = query.filter(SecurityLog.event_type == event_type)
    
    if is_handled is not None:
        query = query.filter(SecurityLog.is_handled == is_handled)
    
    # 关键词搜索（支持事件描述、涉及用户、攻击者 IP）
    if keyword:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                SecurityLog.description.like(f'%{keyword}%'),
                SecurityLog.involved_user.like(f'%{keyword}%'),
                SecurityLog.attacker_ip.like(f'%{keyword}%')
            )
        )
    
    # 分页
    logs = query.order_by(SecurityLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 获取所有事件类型
    events_query = SecurityLog.query.with_entities(
        SecurityLog.event_type
    ).distinct().all()
    event_types = [e[0] for e in events_query]
    
    return render_template('admin/security_logs.html',
                          logs=logs,
                          event_types=event_types,
                          selected_severity=severity,
                          selected_event_type=event_type,
                          selected_is_handled=is_handled,
                          selected_days=days,
                          selected_keyword=keyword)


@audit_bp.route('/security/<int:event_id>/handle', methods=['POST'])
@login_required
@admin_required
def handle_security_event(event_id):
    """处理安全事件"""
    notes = request.form.get('notes')
    
    if AuditService.mark_security_event_handled(event_id, current_user.name, notes):
        flash('✅ 事件已标记为已处理', 'success')
    else:
        flash('❌ 事件不存在', 'error')
    
    return redirect(url_for('audit.security_logs'))


@audit_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """日志统计仪表板"""
    days = request.args.get('days', default=30, type=int)
    
    # 获取基础统计信息
    stats = AuditService.get_statistics(days=days)
    
    # 获取时间段对比数据（本周 vs 上周）
    period_comparison = AuditService.get_period_comparison(days_current=7, days_previous=7)
    
    # 获取用户行为分析数据
    user_behavior = AuditService.get_user_behavior_analysis(days=days)
    
    # 获取问卷题目正确率统计
    question_stats = AuditService.get_question_statistics(days=days)
    
    # 获取最近的操作日志
    recent_logs = AuditService.get_recent_logs(days=7, limit=10)
    
    # 获取未处理的安全事件
    unhandled_events = AuditService.get_security_events(is_handled=False, limit=10)
    
    return render_template('admin/audit_dashboard.html',
                          stats=stats,
                          period_comparison=period_comparison,
                          user_behavior=user_behavior,
                          question_stats=question_stats,
                          recent_logs=recent_logs,
                          unhandled_events=unhandled_events,
                          selected_days=days)


@audit_bp.route('/logs/export')
@login_required
@admin_required
def export_logs():
    """导出操作日志为 CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    from datetime import datetime, timedelta
    from app.models.audit_log import AuditLog
    
    # 获取筛选参数
    user_id = request.args.get('user_id', type=int)
    action_type = request.args.get('action_type')
    status = request.args.get('status')
    days = request.args.get('days', default=30, type=int)
    
    # 构建查询
    query = AuditLog.query
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(AuditLog.created_at >= cutoff_date)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action_type:
        query = query.filter(AuditLog.action_type == action_type)
    
    if status:
        query = query.filter(AuditLog.status == status)
    
    # 获取所有数据
    logs = query.order_by(AuditLog.created_at.desc()).all()
    
    # 创建 CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        'ID', '操作人', '学号', '操作类型', '描述', 'IP 地址',
        '状态', '时间', '错误信息'
    ])
    
    # 写入数据
    for log in logs:
        writer.writerow([
            log.id,
            log.user_name or '未知用户',
            log.student_id or '-',
            log.action_type,
            log.action_description,
            log.ip_address or '-',
            log.status,
            log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            log.error_message or '-'
        ])
    
    # 生成响应
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'audit_logs_{timestamp}.csv'
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    # 记录导出操作
    AuditService.log_user_action(
        user=current_user,
        action_type='EXPORT_LOGS',
        description=f'导出操作日志：{len(logs)} 条记录',
        status='success'
    )
    
    return response


@audit_bp.route('/security/export')
@login_required
@admin_required
def export_security_logs():
    """导出安全日志为 CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    from datetime import datetime, timedelta
    from app.models.security_log import SecurityLog
    
    # 获取筛选参数
    severity = request.args.get('severity')
    event_type = request.args.get('event_type')
    is_handled = request.args.get('is_handled')
    days = request.args.get('days', default=30, type=int)
    
    # 构建查询
    query = SecurityLog.query
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(SecurityLog.created_at >= cutoff_date)
    
    if severity:
        query = query.filter(SecurityLog.severity == severity)
    
    if event_type:
        query = query.filter(SecurityLog.event_type == event_type)
    
    if is_handled is not None:
        query = query.filter(SecurityLog.is_handled == is_handled)
    
    # 获取所有数据
    logs = query.order_by(SecurityLog.created_at.desc()).all()
    
    # 创建 CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        'ID', '事件类型', '描述', '严重程度', '涉及用户', '学号',
        '攻击者 IP', '处理状态', '处理人', '处理时间', '时间'
    ])
    
    # 写入数据
    for log in logs:
        writer.writerow([
            log.id,
            log.event_type,
            log.event_description,
            log.severity,
            log.user_name or '-',
            log.student_id or '-',
            log.attacker_ip or '-',
            '已处理' if log.is_handled else '未处理',
            log.handled_by or '-',
            log.handled_at.strftime('%Y-%m-%d %H:%M:%S') if log.handled_at else '-',
            log.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # 生成响应
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'security_logs_{timestamp}.csv'
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    # 记录导出操作
    AuditService.log_user_action(
        user=current_user,
        action_type='EXPORT_SECURITY_LOGS',
        description=f'导出安全日志：{len(logs)} 条记录',
        status='success'
    )
    
    return response
