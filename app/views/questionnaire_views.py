"""
问卷视图控制器
处理问卷相关的请求
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user
import os
import json
from app.services.assessment_service import AssessmentService
from app.utils.helpers import generate_safe_filename, validate_image_file, ensure_upload_directory
from app.utils.decorators import prevent_duplicate_submission
from app import db

# 创建问卷蓝图
questionnaire_bp = Blueprint(
    'questionnaire', __name__, url_prefix='/questionnaire')


@questionnaire_bp.route('/')
@login_required
def index():
    """
    问卷主页
    显示问卷表单
    """
    return render_template('questionnaire/questionnaire.html')


@questionnaire_bp.route('/submit', methods=['POST'])
@login_required
# @prevent_duplicate_submission(hours=24)  # 防止 24 小时内重复提交
@prevent_duplicate_submission(hours=0)    # 测试用,设置为 0 小时内不能重复提交
def submit():
    """
    提交问卷
    处理问卷提交并进行风险评估
    """
    try:
        # 收集 28 题答案
        answers = {}
        for i in range(1, 29):
            key = f'q{i}'
            val = request.form.get(key, '0')
            try:
                answers[key] = int(val)
            except ValueError:
                answers[key] = 0

        # 收集开放性文本
        open_texts = {
            'open1': request.form.get('open1', '').strip(),
            'open2': request.form.get('open2', '').strip()
        }

        # 处理图片上传
        uploaded_images = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            ensure_upload_directory()

            for file in files:
                if file.filename and validate_image_file(file.filename):
                    # 生成安全的文件名
                    safe_filename = generate_safe_filename(
                        file.filename,
                        prefix=f"{current_user.student_id}_"
                    )

                    if safe_filename:
                        save_path = os.path.join(
                            current_app.config['UPLOAD_FOLDER'],
                            safe_filename
                        )
                        try:
                            file.save(save_path)
                            uploaded_images.append(save_path)
                            print(f"成功保存图片：{save_path}")
                        except Exception as e:
                            print(f"保存失败：{str(e)}")
                            flash(f'保存图片失败：{str(e)}', 'danger')

        # 获取用户 IP 地址
        ip_address = request.remote_addr

        # 处理问卷提交
        assessment_data = AssessmentService.process_questionnaire_submission(
            user_id=current_user.id,
            answers=answers,
            open_texts=open_texts,
            uploaded_images=uploaded_images,
            ip_address=ip_address
        )

        # 将评估结果存储到 session 中
        session['assessment'] = assessment_data

        if uploaded_images:
            flash(f'成功保存 {len(uploaded_images)} 张图片，已用于 AI 分析。', 'success')
        else:
            flash('提交成功，问卷将在 24 小时后才能再次提交', 'info')

        return redirect(url_for('report.view'))

    except Exception as e:
        flash(f'提交问卷时发生错误：{str(e)}', 'danger')
        return redirect(url_for('questionnaire.index'))
