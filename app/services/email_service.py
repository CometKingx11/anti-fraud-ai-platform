"""
邮件发送服务
基于 Flask-Mail 实现邮件通知功能
"""

from flask import current_app, render_template
from flask_mail import Mail, Message
from functools import wraps
import threading

# 创建 Mail 实例
mail = Mail()


class EmailService:
    """邮件服务类"""
    
    @staticmethod
    def send_email(subject, recipients, html_body, text_body=None):
        """
        发送邮件
        
        Args:
            subject (str): 邮件主题
            recipients (list): 收件人列表
            html_body (str): HTML 格式邮件内容
            text_body (str): 纯文本格式邮件内容（可选）
        """
        try:
            # 检查是否配置了邮件服务
            if not current_app.config.get('MAIL_USERNAME'):
                current_app.logger.warning('未配置邮件服务，跳过邮件发送')
                return False
            
            # 创建消息
            msg = Message(
                subject,
                recipients=recipients,
                html=html_body,
                body=text_body
            )
            
            # 异步发送邮件（避免阻塞）
            thread = threading.Thread(
                target=EmailService._send_async_email,
                args=(current_app._get_current_object(), msg)
            )
            thread.start()
            
            current_app.logger.info(f'邮件已发送：{recipients}')
            return True
            
        except Exception as e:
            current_app.logger.error(f'邮件发送失败：{str(e)}')
            return False
    
    @staticmethod
    def _send_async_email(app, msg):
        """异步发送邮件"""
        with app.app_context():
            mail.send(msg)
    
    @staticmethod
    def send_welcome_email(user_email, user_name, student_id):
        """
        发送欢迎邮件（注册成功）
        
        Args:
            user_email (str): 用户邮箱
            user_name (str): 用户姓名
            student_id (str): 学号
        """
        from flask import current_app
        
        try:
            subject = '欢迎加入大学生反诈风险评估平台！'
            
            html_body = f'''
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 欢迎加入反诈评估平台</h1>
                    </div>
                    <div class="content">
                        <p><strong>亲爱的 {user_name} 同学：</strong></p>
                        
                        <p>您好！欢迎加入大学生反诈风险评估平台！</p>
                        
                        <p>您的账号已成功注册：</p>
                        <ul>
                            <li><strong>学号：</strong>{student_id}</li>
                            <li><strong>邮箱：</strong>{user_email}</li>
                        </ul>
                        
                        <p>现在您可以登录系统，进行反诈风险评估测试了。</p>
                        
                        <div style="text-align: center;">
                            <a href="http://127.0.0.1:5000/auth/login" class="button">立即登录</a>
                        </div>
                        
                        <p style="margin-top: 30px;"><strong>温馨提示：</strong></p>
                        <ul>
                            <li>首次登录建议修改初始密码</li>
                            <li>认真填写问卷，获取准确的风险评估</li>
                            <li>定期参加测试，了解自身风险变化</li>
                        </ul>
                        
                        <p style="margin-top: 20px;">祝您学习愉快，远离诈骗！</p>
                        
                        <div class="footer">
                            <p>此邮件由系统自动发送，请勿回复</p>
                            <p>© 2026 大学生反诈风险评估平台</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            text_body = f'''
            亲爱的{user_name}同学：
            
            欢迎加入大学生反诈风险评估平台！
            
            您的账号已成功注册：
            学号：{student_id}
            邮箱：{user_email}
            
            现在您可以登录系统进行评估测试了。
            
            登录地址：http://127.0.0.1:5000/auth/login
            
            温馨提示：
            - 首次登录建议修改初始密码
            - 认真填写问卷，获取准确的风险评估
            - 定期参加测试，了解自身风险变化
            
            祝学习愉快，远离诈骗！
            
            大学生反诈风险评估平台
            '''
            
            return EmailService.send_email(subject, [user_email], html_body, text_body)
            
        except Exception as e:
            current_app.logger.error(f'发送欢迎邮件失败：{str(e)}')
            return False
    
    @staticmethod
    def send_risk_warning_email(user_email, user_name, risk_level, total_score):
        """
        发送风险预警邮件
        
        Args:
            user_email (str): 用户邮箱
            user_name (str): 用户姓名
            risk_level (str): 风险等级
            total_score (int): 风险总分
        """
        from flask import current_app
        
        try:
            subject = '⚠️ 反诈风险预警通知'
            
            # 根据风险等级设置颜色
            color_map = {
                '低风险': '#28a745',
                '中风险': '#ffc107',
                '高风险': '#fd7e14',
                '极高风险': '#dc3545'
            }
            color = color_map.get(risk_level, '#6c757d')
            
            html_body = f'''
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ padding: 30px; background: #f9f9f9; border-radius: 0 0 10px 10px; }}
                    .risk-level {{ display: inline-block; padding: 10px 20px; background: {color}; color: white; border-radius: 5px; font-weight: bold; }}
                    .tips {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>⚠️ 风险预警通知</h2>
                    </div>
                    <div class="content">
                        <p><strong>{user_name} 同学：</strong></p>
                        
                        <p>根据您最新的反诈风险评估结果，系统检测到您的风险等级为：</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <span class="risk-level">{risk_level}</span>
                            <p style="margin-top: 15px;">风险评分：<strong>{total_score} 分</strong></p>
                        </div>
                        
                        <div class="tips">
                            <strong>💡 温馨提示：</strong>
                            <ul>
                                <li>提高警惕，增强防骗意识</li>
                                <li>不轻信陌生来电和短信</li>
                                <li>不随意透露个人信息</li>
                                <li>遇到可疑情况及时报警</li>
                            </ul>
                        </div>
                        
                        <p>建议您：</p>
                        <ol>
                            <li>重新学习反诈知识，提高识别能力</li>
                            <li>向身边人宣传反诈知识</li>
                            <li>定期参加评估测试</li>
                        </ol>
                        
                        <p style="margin-top: 20px;">如有疑问，请联系学校保卫处或辅导员。</p>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            text_body = f'''
            {user_name}同学：
            
            根据您最新的反诈风险评估结果，系统检测到您的风险等级为：{risk_level}
            风险评分：{total_score}分
            
            温馨提示：
            - 提高警惕，增强防骗意识
            - 不轻信陌生来电和短信
            - 不随意透露个人信息
            - 遇到可疑情况及时报警
            
            建议您重新学习反诈知识，提高识别能力。
            
            如有疑问，请联系学校保卫处或辅导员。
            
            大学生反诈风险评估平台
            '''
            
            return EmailService.send_email(subject, [user_email], html_body, text_body)
            
        except Exception as e:
            current_app.logger.error(f'发送风险预警邮件失败：{str(e)}')
            return False
    
    @staticmethod
    def send_password_reset_email(user_email, user_name, new_password):
        """
        发送密码重置邮件
        
        Args:
            user_email (str): 用户邮箱
            user_name (str): 用户姓名
            new_password (str): 新密码
        """
        from flask import current_app
        
        try:
            subject = '🔐 密码重置通知'
            
            html_body = f'''
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #6c757d; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .password {{ background: white; padding: 15px; border: 1px solid #ddd; font-family: monospace; font-size: 18px; text-align: center; margin: 20px 0; }}
                    .warning {{ background: #f8d7da; color: #721c24; padding: 15px; border: 1px solid #f5c6cb; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>🔐 密码重置通知</h2>
                    </div>
                    <div class="content">
                        <p><strong>{user_name} 同学：</strong></p>
                        
                        <p>您的账号密码已被管理员重置。</p>
                        
                        <p>新密码为：</p>
                        <div class="password">{new_password}</div>
                        
                        <div class="warning">
                            <strong>⚠️ 重要提示：</strong>
                            <ul>
                                <li>请立即登录并修改密码</li>
                                <li>不要将密码告诉他人</li>
                                <li>如非本人操作，请立即联系管理员</li>
                            </ul>
                        </div>
                        
                        <p style="margin-top: 20px;">
                            <a href="http://127.0.0.1:5000/auth/login" style="display: inline-block; padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px;">立即登录</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            text_body = f'''
            {user_name}同学：
            
            您的账号密码已被管理员重置。
            
            新密码：{new_password}
            
            重要提示：
            - 请立即登录并修改密码
            - 不要将密码告诉他人
            - 如非本人操作，请立即联系管理员
            
            登录地址：http://127.0.0.1:5000/auth/login
            
            大学生反诈风险评估平台
            '''
            
            return EmailService.send_email(subject, [user_email], html_body, text_body)
            
        except Exception as e:
            current_app.logger.error(f'发送密码重置邮件失败：{str(e)}')
            return False


def init_mail(app):
    """
    初始化邮件服务
    
    Args:
        app: Flask 应用实例
    """
    # 配置 Flask-Mail
    app.config['MAIL_SERVER'] = app.config.get('MAIL_SERVER', 'smtp.qq.com')
    app.config['MAIL_PORT'] = app.config.get('MAIL_PORT', 465)
    app.config['MAIL_USE_SSL'] = app.config.get('MAIL_USE_SSL', True)
    app.config['MAIL_USERNAME'] = app.config.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = app.config.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = app.config.get('MAIL_USERNAME')
    
    # 初始化 Mail
    mail.init_app(app)
