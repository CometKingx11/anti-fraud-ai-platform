"""
模型层测试
测试数据模型的功能和方法
"""

import unittest
import tempfile
import os
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.submission import Submission


class TestUserModel(unittest.TestCase):
    """
    用户模型测试类
    测试User模型的各种功能
    """

    def setUp(self):
        """
        测试准备
        创建临时数据库并初始化应用
        """
        # 创建临时数据库文件
        self.db_fd, self.db_path = tempfile.mkstemp()

        # 创建测试配置
        class TestConfig:
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{self.db_path}'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            SECRET_KEY = 'test-secret-key'
            TESTING = True

        # 创建应用
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

        # 创建数据库表
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

    def test_create_user(self):
        """
        测试创建用户
        """
        user = User(
            student_id='20210001',
            name='张三',
            role='student'
        )
        user.set_password('password123')

        db.session.add(user)
        db.session.commit()

        # 验证用户已保存
        saved_user = User.query.filter_by(student_id='20210001').first()
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.name, '张三')
        self.assertEqual(saved_user.role, 'student')
        self.assertTrue(saved_user.check_password('password123'))

    def test_password_hashing(self):
        """
        测试密码哈希功能
        """
        user = User(student_id='20210002', name='李四')
        user.set_password('original_password')

        # 验证密码哈希
        self.assertNotEqual(user.password_hash, 'original_password')
        self.assertTrue(user.check_password('original_password'))
        self.assertFalse(user.check_password('wrong_password'))

    def test_get_by_student_id(self):
        """
        测试根据学号获取用户
        """
        # 创建用户
        user = User(student_id='20210003', name='王五')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # 测试获取用户
        retrieved_user = User.get_by_student_id('20210003')
        self.assertEqual(retrieved_user.name, '王五')

        # 测试不存在的用户
        non_existent_user = User.get_by_student_id('nonexistent')
        self.assertIsNone(non_existent_user)

    def test_create_user_method(self):
        """
        测试创建用户方法
        """
        user = User.create_user(
            student_id='20210004',
            password='newpassword',
            role='student',
            name='赵六'
        )

        # 验证用户已创建
        self.assertIsNotNone(user.id)
        self.assertEqual(user.student_id, '20210004')
        self.assertEqual(user.name, '赵六')
        self.assertEqual(user.role, 'student')
        self.assertTrue(user.check_password('newpassword'))


class TestSubmissionModel(unittest.TestCase):
    """
    提交记录模型测试类
    测试Submission模型的各种功能
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

        self.app = create_app(TestConfig)
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

    def test_create_submission(self):
        """
        测试创建提交记录
        """
        # 创建关联用户
        user = User(student_id='20210005', name='测试用户')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        # 创建提交记录
        submission = Submission(
            user_id=user.id,
            base_score=60,
            final_score=65,
            risk_level='中风险',
            cognitive=25,
            behavior=25,
            experience=15,
            open_text='这是一个测试',
            risk_points='["风险点1", "风险点2"]',
            analysis='这是分析结果',
            suggestions='["建议1", "建议2"]',
            push_contents='["推送内容1", "推送内容2"]',
            uploaded_images='["path/to/image1.jpg", "path/to/image2.png"]'
        )

        db.session.add(submission)
        db.session.commit()

        # 验证提交记录已保存
        saved_submission = Submission.query.first()
        self.assertIsNotNone(saved_submission)
        self.assertEqual(saved_submission.user_id, user.id)
        self.assertEqual(saved_submission.base_score, 60)
        self.assertEqual(saved_submission.final_score, 65)
        self.assertEqual(saved_submission.risk_level, '中风险')

    def test_to_dict_method(self):
        """
        测试to_dict方法
        """
        # 创建关联用户
        user = User(student_id='20210006', name='测试用户2')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        # 创建提交记录
        submission = Submission(
            user_id=user.id,
            base_score=70,
            final_score=75,
            risk_level='中风险',
            cognitive=30,
            behavior=30,
            experience=15,
            open_text='测试文本',
            risk_points='["风险点A", "风险点B"]',
            analysis='分析文本',
            suggestions='["建议A", "建议B"]',
            push_contents='["推送A", "推送B"]',
            uploaded_images='[]'
        )

        db.session.add(submission)
        db.session.commit()

        # 调用to_dict方法
        data = submission.to_dict()

        # 验证返回的数据
        self.assertEqual(data['user_id'], user.id)
        self.assertEqual(data['student_id'], '20210006')
        self.assertEqual(data['base_score'], 70)
        self.assertEqual(data['final_score'], 75)
        self.assertEqual(data['risk_level'], '中风险')
        self.assertEqual(data['risk_points'], ['风险点A', '风险点B'])
        self.assertEqual(data['suggestions'], ['建议A', '建议B'])
        self.assertEqual(data['push_contents'], ['推送A', '推送B'])

    def test_save_from_dict_method(self):
        """
        测试save_from_dict方法
        """
        # 创建关联用户
        user = User(student_id='20210007', name='测试用户3')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        # 准备数据字典
        data = {
            'user_id': user.id,
            'base_score': 80,
            'final_score': 85,
            'risk_level': '高风险',
            'cognitive': 35,
            'behavior': 35,
            'experience': 15,
            'open_text': '保存测试',
            'risk_points': ['风险点C', '风险点D'],
            'analysis': '分析测试',
            'suggestions': ['建议C', '建议D'],
            'push_contents': ['推送C', '推送D'],
            'uploaded_images': ['img1.jpg', 'img2.png']
        }

        # 使用save_from_dict方法保存
        submission = Submission.save_from_dict(data)

        # 验证保存成功
        self.assertIsNotNone(submission.id)
        self.assertEqual(submission.user_id, user.id)
        self.assertEqual(submission.base_score, 80)
        self.assertEqual(submission.risk_level, '高风险')

        # 验证JSON字段被正确转换为字符串
        self.assertEqual(submission.risk_points, '["风险点C", "风险点D"]')
        self.assertEqual(submission.suggestions, '["建议C", "建议D"]')

    def test_parse_json_field_method(self):
        """
        测试parse_json_field静态方法
        """
        # 测试有效JSON
        valid_json = '["item1", "item2", "item3"]'
        parsed = Submission.parse_json_field(valid_json)
        self.assertEqual(parsed, ['item1', 'item2', 'item3'])

        # 测试无效JSON
        invalid_json = 'invalid json string'
        parsed = Submission.parse_json_field(invalid_json)
        self.assertEqual(parsed, [])

        # 测试None值
        parsed = Submission.parse_json_field(None)
        self.assertEqual(parsed, [])


if __name__ == '__main__':
    unittest.main()
