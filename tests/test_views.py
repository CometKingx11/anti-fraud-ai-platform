"""
视图层测试
测试各个路由端点的功能
"""

import unittest
import tempfile
import os
import json
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.submission import Submission


class TestAuthViews(unittest.TestCase):
    """
    认证视图测试类
    测试登录、登出等功能
    """

    def setUp(self):
        """
        测试准备
        创建临时数据库并初始化应用
        """
        self.db_fd, self.db_path = tempfile.mkstemp()

        class TestConfig:
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{self.db_path}'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            SECRET_KEY = 'test-secret-key'
            TESTING = True
            UPLOAD_FOLDER = tempfile.mkdtemp()

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        """
        测试清理
        删除临时数据库文件
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_login_page(self):
        """
        测试登录页面
        """
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'大学生反诈风险评估平台', response.data)

    def test_login_functionality(self):
        """
        测试登录功能
        """
        # 创建测试用户
        user = User(student_id='20210001', name='测试用户')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # 测试登录
        response = self.client.post('/auth/login', data={
            'student_id': '20210001',
            'password': 'password123'
        }, follow_redirects=True)

        # 验证登录成功（重定向到问卷页面）
        self.assertEqual(response.status_code, 200)
        # 注意：实际的重定向目标取决于路由设置

    def test_invalid_login(self):
        """
        测试无效登录
        """
        response = self.client.post('/auth/login', data={
            'student_id': 'nonexistent',
            'password': 'wrongpassword'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # 验证错误消息
        self.assertIn(b'学号或密码错误', response.data)

    def test_logout(self):
        """
        测试登出功能
        """
        # 首先登录
        user = User(student_id='20210002', name='测试用户2')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['user_id'] = str(user.id)

        # 测试登出
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


class TestQuestionnaireViews(unittest.TestCase):
    """
    问卷视图测试类
    测试问卷相关的路由功能
    """

    def setUp(self):
        """
        测试准备
        """
        self.db_fd, self.db_path = tempfile.mkstemp()

        class TestConfig:
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{self.db_path}'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            SECRET_KEY = 'test-secret-key'
            TESTING = True
            UPLOAD_FOLDER = tempfile.mkdtemp()

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        """
        测试清理
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_questionnaire_index_unauthorized(self):
        """
        测试未授权访问问卷页面
        """
        response = self.client.get('/questionnaire/')
        # 未登录应该重定向到登录页面
        self.assertEqual(response.status_code, 302)  # 重定向

    def test_submit_questionnaire(self):
        """
        测试提交问卷
        """
        # 创建测试用户并登录
        user = User(student_id='20210003', name='测试用户3')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # 模拟登录状态
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['user_id'] = str(user.id)
            sess['role'] = 'student'

        # 准备问卷数据
        answers = {f'q{i}': '3' for i in range(1, 29)}
        open_texts = {'open1': '测试开放题1', 'open2': '测试开放题2'}

        # 合并数据
        data = {**answers, **open_texts}

        # 提交问卷
        response = self.client.post('/questionnaire/submit', data=data,
                                    follow_redirects=True)

        # 验证提交成功（重定向到报告页面）
        self.assertEqual(response.status_code, 200)
        # 验证是否到达报告页面（内容检查）
        # 这里可能需要根据实际模板内容调整

    def test_submit_questionnaire_with_images(self):
        """
        测试提交问卷（带图片上传）
        """
        # 创建测试用户并登录
        user = User(student_id='20210004', name='测试用户4')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['user_id'] = str(user.id)
            sess['role'] = 'student'

        # 创建临时图片文件用于测试
        import io
        from PIL import Image

        # 创建一个简单的图片
        img_byte_arr = io.BytesIO()
        img = Image.new('RGB', (100, 100), color='red')
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        # 准备问卷数据
        answers = {f'q{i}': '3' for i in range(1, 29)}
        open_texts = {'open1': '测试开放题1', 'open2': '测试开放题2'}

        # 合并数据
        data = {**answers, **open_texts, 'images': (img_byte_arr, 'test.jpg')}

        # 提交问卷（带图片）
        response = self.client.post('/questionnaire/submit',
                                    data=data,
                                    content_type='multipart/form-data',
                                    follow_redirects=True)

        self.assertEqual(response.status_code, 200)


class TestReportViews(unittest.TestCase):
    """
    报告视图测试类
    测试报告相关的路由功能
    """

    def setUp(self):
        """
        测试准备
        """
        self.db_fd, self.db_path = tempfile.mkstemp()

        class TestConfig:
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{self.db_path}'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            SECRET_KEY = 'test-secret-key'
            TESTING = True
            UPLOAD_FOLDER = tempfile.mkdtemp()

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        """
        测试清理
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_report_view_unauthorized(self):
        """
        测试未授权访问报告页面
        """
        response = self.client.get('/report/')
        self.assertEqual(response.status_code, 302)  # 重定向到登录

    def test_report_view_with_session_data(self):
        """
        测试有session数据时的报告页面
        """
        # 创建测试用户并登录
        user = User(student_id='20210005', name='测试用户5')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['user_id'] = str(user.id)
            sess['role'] = 'student'
            # 添加评估数据到session
            sess['assessment'] = {
                'student_id': '20210005',
                'base_score': 60,
                'final_score': 65,
                'risk_level': '中风险',
                'cognitive': 25,
                'behavior': 25,
                'experience': 15,
                'open_text': '测试开放文本',
                'risk_points': [],
                'analysis': '测试分析',
                'suggestions': [],
                'push_contents': []
            }

        # 访问报告页面
        response = self.client.get('/report/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'您的反诈风险评估报告', response.data)

    def test_export_pdf_unauthorized(self):
        """
        测试未授权访问PDF导出
        """
        response = self.client.get('/report/export-pdf')
        self.assertEqual(response.status_code, 302)  # 重定向到登录


class TestAdminViews(unittest.TestCase):
    """
    管理员视图测试类
    测试管理员相关的路由功能
    """

    def setUp(self):
        """
        测试准备
        """
        self.db_fd, self.db_path = tempfile.mkstemp()

        class TestConfig:
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{self.db_path}'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            SECRET_KEY = 'test-secret-key'
            TESTING = True
            UPLOAD_FOLDER = tempfile.mkdtemp()

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        """
        测试清理
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_admin_dashboard_unauthorized(self):
        """
        测试未授权访问管理员面板
        """
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # 重定向到登录

    def test_admin_dashboard_as_student(self):
        """
        测试学生身份访问管理员面板
        """
        # 创建学生用户并登录
        user = User(student_id='20210006', name='学生用户', role='student')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['user_id'] = str(user.id)
            sess['role'] = 'student'

        # 尝试访问管理员面板
        response = self.client.get('/admin/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # 验证权限不足的消息
        self.assertIn(b'权限不足', response.data)

    def test_admin_dashboard_as_admin(self):
        """
        测试管理员身份访问管理员面板
        """
        # 创建管理员用户并登录
        admin = User(student_id='admin', name='管理员', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['user_id'] = str(admin.id)
            sess['role'] = 'admin'

        # 访问管理员面板
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'管理员后台', response.data)


class TestIntegration(unittest.TestCase):
    """
    集成测试类
    测试多个组件之间的协作
    """

    def setUp(self):
        """
        测试准备
        """
        self.db_fd, self.db_path = tempfile.mkstemp()

        class TestConfig:
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{self.db_path}'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            SECRET_KEY = 'test-secret-key'
            TESTING = True
            UPLOAD_FOLDER = tempfile.mkdtemp()

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        """
        测试清理
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_complete_workflow(self):
        """
        测试完整的用户工作流程
        登录 -> 填写问卷 -> 查看报告 -> 导出PDF
        """
        # 1. 创建用户
        user = User(student_id='20210007', name='集成测试用户')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # 2. 登录
        login_response = self.client.post('/auth/login', data={
            'student_id': '20210007',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)

        # 3. 访问问卷页面
        questionnaire_response = self.client.get('/questionnaire/')
        self.assertEqual(questionnaire_response.status_code, 200)

        # 4. 提交问卷
        answers = {f'q{i}': '3' for i in range(1, 29)}
        open_texts = {'open1': '集成测试开放题1', 'open2': '集成测试开放题2'}
        data = {**answers, **open_texts}

        submit_response = self.client.post('/questionnaire/submit',
                                           data=data,
                                           follow_redirects=True)
        self.assertEqual(submit_response.status_code, 200)

        # 5. 查看报告
        report_response = self.client.get('/report/')
        self.assertEqual(report_response.status_code, 200)

        # 6. 尝试导出PDF（这里主要是测试路由可达性）
        pdf_response = self.client.get('/report/export-pdf')
        # 导出PDF可能因为session中没有数据而重定向
        self.assertIn(pdf_response.status_code, [200, 302])


if __name__ == '__main__':
    unittest.main()
