"""
应用启动文件
负责创建应用实例并运行服务器
"""

from app import create_app
from config.settings import config
import os


# 获取配置环境
config_name = os.environ.get('FLASK_ENV', 'default')

# 创建应用实例
app = create_app(config[config_name])


if __name__ == '__main__':
    # 运行应用
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=config_name == 'development'
    )
