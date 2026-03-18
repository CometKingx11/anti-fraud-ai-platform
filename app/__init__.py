# Author: 小土豆233
# Date: 2026-03-16 23:42:18
# LastEditTime: 2026-03-16 23:42:27
# LastEditors: 小土豆233
# Description: Flask 反诈风险评估系统主应用入口
# 采用 MVC 架构，实现了模块化设计
# FilePath: flask_anti_project\app\__init__.py

from config.settings import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


# 初始化扩展组件
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_class=Config):
    """
    应用工厂函数
    创建并配置 Flask 应用实例

    Args:
        config_class: 配置类，默认为 Config

    Returns:
        Flask: 配置好的 Flask 应用实例
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # 注入 csrf_token 到模板上下文
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        # 使用 lambda 包装，确保在模板中调用时生成 token
        return dict(csrf_token=lambda: generate_csrf())

    # 设置登录管理器配置
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'warning'

    # 配置用户加载函数
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # 注册蓝图
    register_blueprints(app)
    
    # 注册根路径路由
    @app.route('/')
    def index():
        """根路径重定向到登录页面"""
        return redirect(url_for('auth.login'))

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app


def register_blueprints(app):
    """
    注册应用蓝图
    将不同功能模块的视图注册到应用中

    Args:
        app: Flask 应用实例
    """
    from app.views.auth_views import auth_bp
    from app.views.questionnaire_views import questionnaire_bp
    from app.views.report_views import report_bp
    from app.views.admin_views import admin_bp
    from app.views.questionnaire_mgmt_views import questionnaire_mgmt_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(questionnaire_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(questionnaire_mgmt_bp)
