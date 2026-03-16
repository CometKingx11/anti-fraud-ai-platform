# Author: 小土豆233
# Date: 2026-03-17 00:02:44
# LastEditTime: 2026-03-17 00:12:23
# LastEditors: 小土豆233
# Description:
# FilePath: flask_anti_project\app\utils\helpers.py
"""
工具函数模块
提供各种通用的辅助函数
"""

import os
import re
from datetime import datetime
from flask import current_app


def validate_student_id(student_id):
    """
    验证学号格式

    Args:
        student_id (str): 待验证的学号

    Returns:
        bool: 学号格式是否正确
    """
    if not student_id:
        return False

    # 学号应为数字组成的字符串，长度通常为8-12位
    pattern = r'^\d{8,12}$'
    return bool(re.match(pattern, student_id))


def validate_image_file(filename):
    """
    验证图片文件格式

    Args:
        filename (str): 文件名

    Returns:
        bool: 文件格式是否允许
    """
    if not filename:
        return False

    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    _, ext = os.path.splitext(filename.lower())
    return ext in allowed_extensions


def generate_safe_filename(original_filename, prefix=''):
    """
    生成安全的文件名

    Args:
        original_filename (str): 原始文件名
        prefix (str): 文件前缀

    Returns:
        str: 安全的文件名
    """
    if not original_filename:
        return None

    # 移除危险字符
    safe_chars = re.sub(r'[^\w\-_.]', '_', original_filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    name, ext = os.path.splitext(safe_chars)
    return f"{prefix}{name}_{timestamp}{ext}"


def ensure_upload_directory():
    """
    确保上传目录存在
    """
    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)


def format_datetime(dt, fmt='%Y-%m-%d %H:%M'):
    """
    格式化日期时间

    Args:
        dt (datetime): 日期时间对象
        fmt (str): 格式字符串

    Returns:
        str: 格式化后的日期时间字符串
    """
    if not dt:
        return ''
    return dt.strftime(fmt)
