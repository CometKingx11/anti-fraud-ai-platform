"""
问卷管理视图
提供问卷题目配置、编辑、删除等功能
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.utils.decorators import role_required
from app import db
from app.models.questionnaire import QuestionnaireQuestion, QuestionnaireConfig
import json

questionnaire_mgmt_bp = Blueprint('questionnaire_mgmt', __name__, url_prefix='/admin/questionnaire')


@questionnaire_mgmt_bp.route('/')
@login_required
@role_required('admin')
def question_list():
    """问卷题目列表"""
    category = request.args.get('category', '')
    
    if category:
        questions = QuestionnaireQuestion.query.filter_by(
            category=category
        ).order_by(QuestionnaireQuestion.display_order, QuestionnaireQuestion.question_number).all()
    else:
        questions = QuestionnaireQuestion.query.order_by(
            QuestionnaireQuestion.display_order, 
            QuestionnaireQuestion.question_number
        ).all()
    
    return render_template('admin/question_list.html', questions=questions, current_category=category)


@questionnaire_mgmt_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_question():
    """创建新题目"""
    if request.method == 'POST':
        try:
            question = QuestionnaireQuestion(
                question_number=int(request.form['question_number']),
                category=request.form['category'],
                question_text=request.form['question_text'],
                min_score=int(request.form['min_score']),
                max_score=int(request.form['max_score']),
                dimension=request.form['dimension'],
                weight=float(request.form.get('weight', 1.0)),
                options_json=request.form.get('options_json', ''),
                is_active=request.form.get('is_active') == 'on',
                is_required=request.form.get('is_required') == 'on',
                display_order=int(request.form.get('display_order', 0))
            )
            
            db.session.add(question)
            db.session.commit()
            
            # 记录操作日志
            from app.services.audit_service import AuditService
            from flask_login import current_user
            AuditService.log_user_action(
                user=current_user,
                action_type='CREATE_QUESTION',
                description=f'创建问卷题目：{question.question_text[:50]}...',
                status='success',
                target_type='QuestionnaireQuestion',
                target_id=question.id,
                extra_data={'question_number': question.question_number, 'category': question.category}
            )
            
            flash('题目创建成功', 'success')
            return redirect(url_for('questionnaire_mgmt.question_list'))
            
        except Exception as e:
            db.session.rollback()
            # 记录错误日志
            from app.services.audit_service import AuditService
            from flask_login import current_user
            AuditService.log_user_action(
                user=current_user,
                action_type='CREATE_QUESTION',
                description=f'创建问卷题目失败：{str(e)}',
                status='error',
                extra_data={'error': str(e)}
            )
            flash(f'创建失败：{str(e)}', 'error')
    
    return render_template('admin/question_form.html', action='create', question=None)


@questionnaire_mgmt_bp.route('/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_question(question_id):
    """编辑题目"""
    question = QuestionnaireQuestion.query.get_or_404(question_id)
    
    if request.method == 'POST':
        try:
            old_text = question.question_text
            question.question_number = int(request.form['question_number'])
            question.category = request.form['category']
            question.question_text = request.form['question_text']
            question.min_score = int(request.form['min_score'])
            question.max_score = int(request.form['max_score'])
            question.dimension = request.form['dimension']
            question.weight = float(request.form.get('weight', 1.0))
            question.options_json = request.form.get('options_json', '')
            question.is_active = request.form.get('is_active') == 'on'
            question.is_required = request.form.get('is_required') == 'on'
            question.display_order = int(request.form.get('display_order', 0))
            
            db.session.commit()
            
            # 记录操作日志
            from app.services.audit_service import AuditService
            from flask_login import current_user
            AuditService.log_user_action(
                user=current_user,
                action_type='UPDATE_QUESTION',
                description=f'更新问卷题目：{old_text[:30]}... -> {question.question_text[:30]}...',
                status='success',
                target_type='QuestionnaireQuestion',
                target_id=question.id,
                extra_data={'question_number': question.question_number}
            )
            
            flash('题目更新成功', 'success')
            return redirect(url_for('questionnaire_mgmt.question_list'))
            
        except Exception as e:
            db.session.rollback()
            # 记录错误日志
            from app.services.audit_service import AuditService
            from flask_login import current_user
            AuditService.log_user_action(
                user=current_user,
                action_type='UPDATE_QUESTION',
                description=f'更新问卷题目失败：{str(e)}',
                status='error',
                extra_data={'error': str(e)}
            )
            flash(f'更新失败：{str(e)}', 'error')
    
    return render_template('admin/question_form.html', action='edit', question=question)


@questionnaire_mgmt_bp.route('/import', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def import_questions():
    """批量导入题目"""
    if request.method == 'POST':
        # 检查是否有上传文件
        if 'file' not in request.files:
            flash('请选择要上传的文件', 'danger')
            return redirect(url_for('questionnaire_mgmt.import_questions'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('未选择文件', 'danger')
            return redirect(url_for('questionnaire_mgmt.import_questions'))
        
        # 检查文件扩展名（支持 CSV 和 XLSX）
        if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            try:
                from app.services.batch_question_service import import_questions_from_file
                import os
                from werkzeug.utils import secure_filename
                
                # 保存上传的文件
                uploads_dir = os.path.join(os.getcwd(), 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                filename = secure_filename(file.filename)
                file_path = os.path.join(uploads_dir, filename)
                file.save(file_path)
                
                # 导入题目
                result = import_questions_from_file(file_path)
                
                # 删除临时文件
                try:
                    os.remove(file_path)
                except:
                    pass
                
                # 记录操作日志
                from app.services.audit_service import AuditService
                from flask_login import current_user
                AuditService.log_user_action(
                    user=current_user,
                    action_type='BATCH_IMPORT_QUESTIONS',
                    description=f'批量导入问卷题目：成功{result["success"]}道，失败{result["failed"]}道',
                    status='success' if result['success'] > 0 else 'error',
                    extra_data={'success': result['success'], 'failed': result['failed'], 'filename': filename}
                )
                
                # 显示结果
                if result['success'] > 0:
                    flash(f"✅ 成功导入 {result['success']} 道题目", 'success')
                
                if result['failed'] > 0:
                    flash(f"⚠️ 失败 {result['failed']} 道题目", 'warning')
                    for error in result['errors'][:5]:  # 只显示前 5 个错误
                        flash(f"  - {error}", 'danger')
                    
                    if len(result['errors']) > 5:
                        flash(f"  ... 还有 {len(result['errors']) - 5} 个错误", 'warning')
                
                return redirect(url_for('questionnaire_mgmt.question_list'))
                
            except Exception as e:
                # 记录错误日志
                from app.services.audit_service import AuditService
                from flask_login import current_user
                AuditService.log_user_action(
                    user=current_user,
                    action_type='BATCH_IMPORT_QUESTIONS',
                    description=f'批量导入问卷题目失败：{str(e)}',
                    status='error',
                    extra_data={'error': str(e)}
                )
                flash(f'导入失败：{str(e)}', 'danger')
        else:
            flash('不支持的文件格式，请上传 CSV 或 Excel 文件', 'danger')
    
    return render_template('admin/question_import.html')


@questionnaire_mgmt_bp.route('/<int:question_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_question(question_id):
    """删除题目"""
    try:
        question = QuestionnaireQuestion.query.get_or_404(question_id)
        question_text = question.question_text
        
        db.session.delete(question)
        db.session.commit()
        
        # 记录操作日志
        from app.services.audit_service import AuditService
        from flask_login import current_user
        AuditService.log_user_action(
            user=current_user,
            action_type='DELETE_QUESTION',
            description=f'删除问卷题目：{question_text[:50]}...',
            status='success',
            target_type='QuestionnaireQuestion',
            target_id=question_id,
            extra_data={'question_number': question.question_number}
        )
        
        flash('题目删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        # 记录错误日志
        from app.services.audit_service import AuditService
        from flask_login import current_user
        AuditService.log_user_action(
            user=current_user,
            action_type='DELETE_QUESTION',
            description=f'删除问卷题目失败：{str(e)}',
            status='error',
            extra_data={'error': str(e)}
        )
        flash(f'删除失败：{str(e)}', 'error')
    
    return redirect(url_for('questionnaire_mgmt.question_list'))


@questionnaire_mgmt_bp.route('/toggle-status/<int:question_id>', methods=['POST'])
@login_required
@role_required('admin')
def toggle_question_status(question_id):
    """切换题目启用状态"""
    question = QuestionnaireQuestion.query.get_or_404(question_id)
    question.is_active = not question.is_active
    db.session.commit()
    
    status = '启用' if question.is_active else '禁用'
    flash(f'题目已{status}', 'success')
    
    return redirect(url_for('questionnaire_mgmt.question_list'))


@questionnaire_mgmt_bp.route('/config', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def config():
    """问卷全局配置"""
    if request.method == 'POST':
        # 保存配置项
        for key in request.form.keys():
            if key.startswith('config_'):
                config_key = key.replace('config_', '')
                config_value = request.form[key]
                config_desc = request.form.get(f'desc_{config_key}', '')
                QuestionnaireConfig.set_config(config_key, config_value, config_desc)
        
        flash('配置保存成功', 'success')
        return redirect(url_for('questionnaire_mgmt.config'))
    
    # 获取所有配置
    configs = QuestionnaireConfig.query.all()
    config_dict = {c.config_key: c.config_value for c in configs}
    
    return render_template('admin/questionnaire_config.html', configs=config_dict)


@questionnaire_mgmt_bp.route('/api/questions')
@login_required
def api_get_questions():
    """API：获取问卷题目（供学生端使用）"""
    category = request.args.get('category', '')
    questions = QuestionnaireQuestion.get_active_questions(category)
    
    return jsonify({
        'success': True,
        'data': [q.to_dict() for q in questions]
    })
