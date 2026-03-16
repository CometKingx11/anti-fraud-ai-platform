"""
项目配置文件
定义了开发、测试和生产环境的配置参数
"""

import os
from dotenv import load_dotenv
import secrets

load_dotenv()


class Config:
    """基础配置类"""

    # 应用密钥 - 优先从环境变量获取，否则生成随机密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///anti_fraud.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 上传文件配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制文件大小为16MB

    # DashScope API配置
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY')

    # 分页配置
    PER_PAGE = 10

    # 会话配置
    SESSION_COOKIE_SECURE = False  # 在开发环境中设为False，生产环境应设为True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # 静态文件缓存配置
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1年

    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    # 邮件配置（如果需要）
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in [
        'true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # 时区配置
    TIMEZONE = os.environ.get('TIMEZONE', 'Asia/Shanghai')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL') or 'sqlite:///anti_fraud_dev.db'
    # 在开发环境中允许不安全的会话cookie
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///anti_fraud_prod.db'
    # 在生产环境中强制使用安全的会话cookie
    SESSION_COOKIE_SECURE = True

    # 生产环境特定配置
    LOG_LEVEL = 'WARNING'

    # 安全配置
    PREFERRED_URL_SCHEME = 'https'

    # 缓存配置
    CACHE_TYPE = 'simple'  # 或者使用 'redis', 'memcached' 等

    # 数据库连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True
    }


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 使用内存数据库
    WTF_CSRF_ENABLED = False  # 禁用CSRF保护以便测试
    DEBUG = True

    # 测试特定配置
    UPLOAD_FOLDER = '/tmp/test_uploads'  # 使用临时目录
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB限制用于测试


class StagingConfig(Config):
    """预发布环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'STAGING_DATABASE_URL') or 'sqlite:///anti_fraud_staging.db'
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'INFO'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """
    根据环境变量获取配置

    Returns:
        Config: 对应环境的配置类
    """
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])


def validate_config():
    """
    验证配置的有效性

    Raises:
        ValueError: 如果配置无效则抛出异常
    """
    # 检查必需的配置项
    required_configs = ['SECRET_KEY']

    for config_name in required_configs:
        config_value = getattr(get_config(), config_name, None)
        if not config_value:
            raise ValueError(f"缺少必需的配置项: {config_name}")

    # 检查数据库URL格式
    database_url = get_config().SQLALCHEMY_DATABASE_URI
    if not database_url:
        raise ValueError("数据库URL未配置")

    # 检查上传目录是否存在或可创建
    upload_folder = get_config().UPLOAD_FOLDER
    try:
        os.makedirs(upload_folder, exist_ok=True)
    except PermissionError:
        raise ValueError(f"无法创建上传目录: {upload_folder}")


def print_config_info():
    """
    打印当前配置信息（仅用于调试）
    """
    current_config = get_config()
    print(f"当前环境: {os.environ.get('FLASK_ENV', 'default')}")
    print(f"调试模式: {current_config.DEBUG}")
    print(f"数据库URL: {current_config.SQLALCHEMY_DATABASE_URI}")
    print(f"上传目录: {current_config.UPLOAD_FOLDER}")
    print(
        f"DASHSCOPE_API_KEY: {'已配置' if current_config.DASHSCOPE_API_KEY else '未配置'}")


if __name__ == "__main__":
    # 如果直接运行此文件，打印配置信息
    print_config_info()
