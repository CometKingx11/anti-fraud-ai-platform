"""
评分规则管理视图
支持管理员手动调整评分规则、权重、风险阈值等
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.utils.decorators import role_required
from app import db
from app.models.questionnaire import QuestionnaireQuestion, QuestionnaireConfig
import json

scoring_rules_bp = Blueprint('scoring_rules', __name__, url_prefix='/admin/scoring-rules')


@scoring_rules_bp.route('/')
@login_required
@role_required('admin')
def index():
    """评分规则管理首页"""
    # 获取所有题目
    questions = QuestionnaireQuestion.query.order_by(
        QuestionnaireQuestion.display_order, 
        QuestionnaireQuestion.question_number
    ).all()
    
    # 获取当前配置的风险阈值
    threshold_low = QuestionnaireConfig.get_int_config('threshold_low', 30)
    threshold_mid = QuestionnaireConfig.get_int_config('threshold_mid', 55)
    threshold_high = QuestionnaireConfig.get_int_config('threshold_high', 80)
    
    # 获取维度满分配置
    max_cognitive = QuestionnaireConfig.get_int_config('max_cognitive', 40)
    max_behavior = QuestionnaireConfig.get_int_config('max_behavior', 40)
    max_experience = QuestionnaireConfig.get_int_config('max_experience', 20)
    
    return render_template(
        'admin/scoring_rules.html',
        questions=questions,
        threshold_low=threshold_low,
        threshold_mid=threshold_mid,
        threshold_high=threshold_high,
        max_cognitive=max_cognitive,
        max_behavior=max_behavior,
        max_experience=max_experience
    )


@scoring_rules_bp.route('/update-weights', methods=['POST'])
@login_required
@role_required('admin')
def update_weights():
    """批量更新题目权重"""
    try:
        data = request.get_json()
        weights = data.get('weights', {})
        
        updated_count = 0
        for question_id, weight in weights.items():
            question = QuestionnaireQuestion.query.get(int(question_id))
            if question:
                old_weight = question.weight
                question.weight = float(weight)
                updated_count += 1
        
        db.session.commit()
        
        # 记录操作日志
        from app.services.audit_service import AuditService
        from flask_login import current_user
        AuditService.log_user_action(
            user=current_user,
            action_type='UPDATE_SCORING_WEIGHTS',
            description=f'批量更新评分权重：共{updated_count}个题目',
            status='success',
            extra_data={'updated_count': updated_count, 'weights': weights}
        )
        
        flash(f'✅ 成功更新 {updated_count} 个题目的权重', 'success')
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        # 记录错误日志
        from app.services.audit_service import AuditService
        from flask_login import current_user
        AuditService.log_user_action(
            user=current_user,
            action_type='UPDATE_SCORING_WEIGHTS',
            description=f'批量更新评分权重失败：{str(e)}',
            status='error',
            extra_data={'error': str(e)}
        )
        flash(f'❌ 更新失败：{str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400


@scoring_rules_bp.route('/update-thresholds', methods=['POST'])
@login_required
@role_required('admin')
def update_thresholds():
    """更新风险阈值"""
    try:
        threshold_low = int(request.form.get('threshold_low', 30))
        threshold_mid = int(request.form.get('threshold_mid', 55))
        threshold_high = int(request.form.get('threshold_high', 80))
        
        # 验证阈值逻辑
        if not (0 <= threshold_low <= threshold_mid <= threshold_high <= 130):
            flash('❌ 阈值设置不合理：必须满足 0 ≤ 低风险 ≤ 中风险 ≤ 高风险 ≤ 130', 'danger')
            return redirect(url_for('scoring_rules.index'))
        
        # 保存配置
        QuestionnaireConfig.set_config('threshold_low', str(threshold_low), '低风险阈值上限')
        QuestionnaireConfig.set_config('threshold_mid', str(threshold_mid), '中风险阈值上限')
        QuestionnaireConfig.set_config('threshold_high', str(threshold_high), '高风险阈值上限')
        
        # 记录操作日志
        from app.services.audit_service import AuditService
        from flask_login import current_user
        AuditService.log_user_action(
            user=current_user,
            action_type='UPDATE_RISK_THRESHOLDS',
            description=f'更新风险阈值：低={threshold_low}, 中={threshold_mid}, 高={threshold_high}',
            status='success',
            extra_data={'threshold_low': threshold_low, 'threshold_mid': threshold_mid, 'threshold_high': threshold_high}
        )
        
        flash('✅ 风险阈值更新成功', 'success')
        return redirect(url_for('scoring_rules.index'))
    
    except Exception as e:
        db.session.rollback()
        # 记录错误日志
        from app.services.audit_service import AuditService
        from flask_login import current_user
        AuditService.log_user_action(
            user=current_user,
            action_type='UPDATE_RISK_THRESHOLDS',
            description=f'更新风险阈值失败：{str(e)}',
            status='error',
            extra_data={'error': str(e)}
        )
        flash(f'❌ 更新失败：{str(e)}', 'danger')
        return redirect(url_for('scoring_rules.index'))


@scoring_rules_bp.route('/update-dimension-max', methods=['POST'])
@login_required
@role_required('admin')
def update_dimension_max():
    """更新维度满分值"""
    try:
        max_cognitive = int(request.form.get('max_cognitive', 40))
        max_behavior = int(request.form.get('max_behavior', 40))
        max_experience = int(request.form.get('max_experience', 20))
        
        # 验证合理性
        total_max = max_cognitive + max_behavior + max_experience
        if total_max > 130:
            flash(f'❌ 维度满分总和 ({total_max}) 超过总分上限 (130)', 'danger')
            return redirect(url_for('scoring_rules.index'))
        
        # 保存配置
        QuestionnaireConfig.set_config('max_cognitive', str(max_cognitive), '认知维度满分')
        QuestionnaireConfig.set_config('max_behavior', str(max_behavior), '行为维度满分')
        QuestionnaireConfig.set_config('max_experience', str(max_experience), '经历维度满分')
        
        flash('✅ 维度满分值更新成功', 'success')
        return redirect(url_for('scoring_rules.index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'❌ 更新失败：{str(e)}', 'danger')
        return redirect(url_for('scoring_rules.index'))


@scoring_rules_bp.route('/reset-question/<int:question_id>', methods=['POST'])
@login_required
@role_required('admin')
def reset_question_weight(question_id):
    """重置单个题目的权重为默认值"""
    try:
        question = QuestionnaireQuestion.query.get_or_404(question_id)
        question.weight = 1.0
        db.session.commit()
        flash('✅ 权重已重置为 1.0', 'success')
        return redirect(url_for('scoring_rules.index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'❌ 重置失败：{str(e)}', 'danger')
        return redirect(url_for('scoring_rules.index'))


@scoring_rules_bp.route('/api/preview-score', methods=['POST'])
@login_required
@role_required('admin')
def preview_score():
    """预览评分效果（使用新规则计算历史数据）"""
    try:
        data = request.get_json()
        submission_ids = data.get('submission_ids', [])
        
        if not submission_ids:
            return jsonify({
                'success': False,
                'error': '请选择至少一条提交记录'
            }), 400
        
        # 获取提交记录
        from app.models.submission import Submission
        submissions = Submission.query.filter(
            Submission.id.in_(submission_ids)
        ).all()
        
        # 这里可以添加新的评分逻辑进行对比
        # 目前仅返回基本信息
        preview_data = []
        for sub in submissions:
            preview_data.append({
                'id': sub.id,
                'student_id': sub.user.student_id if sub.user else 'Unknown',
                'old_score': sub.base_score,
                'old_risk_level': sub.risk_level,
                'new_score': '待计算',
                'new_risk_level': '待计算'
            })
        
        return jsonify({
            'success': True,
            'data': preview_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
