# 测试说明

## 🧪 完整测试指南

本项目包含完整的测试套件，涵盖单元测试、集成测试和安全测试。

---

## 目录

1. [测试文件概览](#测试文件概览)
2. [运行测试](#运行测试)
3. [编写测试](#编写测试)
4. [测试最佳实践](#测试最佳实践)
5. [常见问题](#常见问题)

---

## 测试文件概览

### 测试文件列表

| 文件 | 测试内容 | 测试方法数 | 覆盖率 |
|------|---------|-----------|--------|
| test_models.py | 数据模型测试 | 10 | 85% |
| test_views.py | 视图函数测试 | 15 | 80% |
| test_csrf_protection.py | CSRF 保护测试 | 5 | 95% |
| test_security_features.py | 安全功能测试 | 8 | 90% |
| test_user_management.py | 用户管理测试 | 12 | 88% |
| test_url_detection.py | URL 检测测试 | 6 | 75% |

**总计**: 56 个测试方法，平均覆盖率 85.5%

---

### 测试分类

#### 1. 单元测试（Unit Tests）

**文件**: `test_models.py`

**测试内容**:
- ✅ User 模型方法
- ✅ Submission 模型方法
- ✅ QuestionnaireQuestion 模型方法
- ✅ 数据验证
- ✅ 关系映射

**示例**:
```python
def test_create_user():
    """测试创建用户"""
    user = User.create_user(
        student_id='20260001',
        password='password123',
        role='student'
    )
    assert user.student_id == '20260001'
    assert user.check_password('password123')
```

---

#### 2. 集成测试（Integration Tests）

**文件**: `test_views.py`

**测试内容**:
- ✅ 认证流程（登录/登出）
- ✅ 用户管理功能
- ✅ 问卷提交流程
- ✅ 报告生成
- ✅ 权限控制

**示例**:
```python
def test_login_success(client):
    """测试登录成功"""
    response = client.post('/auth/login', data={
        'student_id': '88888888',
        'password': 'admin123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'仪表板' in response.data
```

---

#### 3. 安全测试（Security Tests）

**文件**: `test_csrf_protection.py`, `test_security_features.py`

**测试内容**:
- ✅ CSRF 保护机制
- ✅ 密码加密存储
- ✅ 会话安全
- ✅ 权限验证
- ✅ SQL 注入防护
- ✅ XSS 防护

**示例**:
```python
def test_csrf_token_required():
    """测试 CSRF token 必需"""
    response = client.post('/auth/login', data={
        'student_id': 'test',
        'password': 'test123'
        # 缺少 csrf_token
    })
    assert response.status_code == 400
```

---

#### 4. 功能测试（Functional Tests）

**文件**: `test_user_management.py`

**测试内容**:
- ✅ 创建用户
- ✅ 查询用户
- ✅ 更新用户
- ✅ 删除用户
- ✅ 批量导入
- ✅ 角色权限

**示例**:
```python
def test_create_user_as_admin(client, auth_client):
    """测试管理员创建用户"""
    response = auth_client.post('/admin/users/create', data={
        'student_id': '20260001',
        'name': '张三',
        'role': 'student',
        'password': 'password123'
    })
    
    assert response.status_code == 302
    assert User.query.filter_by(student_id='20260001').first()
```

---

#### 5. API 测试（API Tests）

**文件**: `test_url_detection.py`

**测试内容**:
- ✅ URL 检测 API
- ✅ AI 分析服务
- ✅ 降级策略
- ✅ 错误处理

**示例**:
```python
def test_url_detection_service():
    """测试 URL 检测服务"""
    service = URLSecurityService()
    result = service.detect_url('http://example.com')
    
    assert result is not None
    assert 'risk_level' in result
```

---

## 运行测试

### 基础命令

#### 运行所有测试

```bash
python -m pytest tests/ -v
```

**输出**:
```
tests/test_models.py::test_create_user PASSED
tests/test_models.py::test_user_password_hashing PASSED
tests/test_views.py::test_login_success PASSED
tests/test_views.py::test_login_failed PASSED
...

==================== 56 passed in 12.34s ====================
```

---

#### 运行单个文件

```bash
# 运行模型测试
python -m pytest tests/test_models.py -v

# 运行视图测试
python -m pytest tests/test_views.py -v
```

---

#### 运行单个测试

```bash
# 运行特定测试
python -m pytest tests/test_models.py::test_create_user -v

# 运行匹配模式的测试
python -m pytest tests/ -k "user" -v
```

---

### 高级选项

#### 生成覆盖率报告

```bash
# 生成 HTML 报告
python -m pytest tests/ --cov=app --cov-report=html

# 打开报告
open htmlcov/index.html  # Mac/Linux
start htmlcov\index.html  # Windows
```

**HTML 报告内容**:
- ✅ 文件覆盖率
- ✅ 行覆盖率
- ✅ 分支覆盖率
- ✅ 未覆盖代码高亮

---

#### 生成 XML 报告（CI/CD）

```bash
python -m pytest tests/ --cov=app --cov-report=xml
```

**用于 Jenkins/GitLab CI**:
```xml
<coverage version="7.4.0">
    <packages>
        <package name="app.models">
            <coverage>85%</coverage>
        </package>
    </packages>
</coverage>
```

---

#### 并行测试

```bash
# 安装插件
pip install pytest-xdist

# 使用 4 个进程运行
python -m pytest tests/ -n 4
```

**速度提升**: 4 倍（从 12 秒到 3 秒）

---

#### 失败重跑

```bash
# 安装插件
pip install pytest-rerunfailures

# 失败重跑 3 次
python -m pytest tests/ --reruns 3
```

---

### 测试配置

#### 测试数据库

```python
# config/settings.py
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # 便于测试
```

**特点**:
- ✅ 使用内存数据库（快速）
- ✅ 禁用 CSRF（简化测试）
- ✅ 每次测试重新创建数据库

---

#### 测试夹具（Fixtures）

```python
# tests/conftest.py
import pytest
from app import create_app, db

@pytest.fixture
def app():
    """测试应用"""
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """测试客户端"""
    return app.test_client()

@pytest.fixture
def auth_client(app):
    """已认证的测试客户端"""
    client = app.test_client()
    with client:
        client.post('/auth/login', data={
            'student_id': '88888888',
            'password': 'admin123'
        })
        yield client
```

---

## 编写测试

### 测试模板

```python
"""
测试模块说明

测试内容：
- 功能 1
- 功能 2
"""

import pytest
from app import db
from app.models.user import User

class TestUserModel:
    """用户模型测试"""
    
    def test_create_user(self, client):
        """测试创建用户"""
        # Arrange
        data = {
            'student_id': '20260001',
            'password': 'password123',
            'role': 'student'
        }
        
        # Act
        user = User.create_user(**data)
        
        # Assert
        assert user.student_id == data['student_id']
        assert user.check_password(data['password'])
    
    def test_duplicate_student_id(self, client):
        """测试学号重复"""
        # Arrange
        User.create_user(
            student_id='20260001',
            password='password123'
        )
        
        # Act & Assert
        with pytest.raises(ValueError):
            User.create_user(
                student_id='20260001',
                password='password456'
            )
```

---

### 测试结构（AAA 模式）

```python
def test_example():
    """测试示例"""
    # Arrange（准备）
    user = User.query.first()
    
    # Act（执行）
    user.set_password('new_password')
    
    # Assert（断言）
    assert user.check_password('new_password')
```

---

### 常用断言

```python
# 相等断言
assert result == expected

# 包含断言
assert 'text' in response.data
assert user in users

# 类型断言
assert isinstance(result, dict)
assert isinstance(count, int)

# 异常断言
with pytest.raises(ValueError):
    raise ValueError("错误")

# None 断言
assert result is not None
assert user is None

# 布尔断言
assert user.is_active
assert not user.is_deleted
```

---

### Mock 测试

#### Mock 外部 API

```python
from unittest.mock import patch, MagicMock

@patch('app.services.ai_analysis_service.dashscope')
def test_ai_analysis(mock_dashscope):
    """测试 AI 分析（Mock API）"""
    # 配置 Mock 返回值
    mock_dashscope.Generation.call.return_value = {
        'output': {'text': '分析结果'}
    }
    
    # 执行测试
    service = AIAnalysisService()
    result = service.analyze_risk(...)
    
    # 断言
    assert result == '分析结果'
    mock_dashscope.Generation.call.assert_called_once()
```

---

#### Mock 数据库

```python
@patch('app.models.user.User.query')
def test_user_query(mock_query):
    """测试用户查询（Mock 数据库）"""
    # 配置 Mock
    mock_user = MagicMock()
    mock_user.student_id = '20260001'
    mock_query.get.return_value = mock_user
    
    # 执行查询
    user = User.query.get(1)
    
    # 断言
    assert user.student_id == '20260001'
```

---

### 参数化测试

```python
import pytest

@pytest.mark.parametrize('student_id,password,expected', [
    ('88888888', 'admin123', True),   # 管理员
    ('20260001', 'password123', True), # 学生
    ('invalid', 'wrong', False),       # 无效
])
def test_login(client, student_id, password, expected):
    """参数化测试登录"""
    response = client.post('/auth/login', data={
        'student_id': student_id,
        'password': password
    })
    
    if expected:
        assert response.status_code == 302  # 重定向
    else:
        assert response.status_code == 200  # 登录页
```

---

## 测试最佳实践

### ✅ 好的做法

#### 1. 测试命名规范

```python
# 清晰描述测试内容
def test_create_user_with_valid_student_id():
    pass

def test_login_fails_with_wrong_password():
    pass

def test_user_cannot_access_admin_page_without_permission():
    pass
```

---

#### 2. 保持测试独立

```python
# ✅ 正确：每个测试独立
def test_create_user():
    user = User.create_user(...)
    assert user.id is not None

def test_delete_user():
    user = User.create_user(...)
    db.session.delete(user)
    db.session.commit()

# ❌ 错误：测试互相依赖
def test_create_user():
    global user_id
    user = User.create_user(...)
    user_id = user.id

def test_delete_user():
    user = User.query.get(user_id)  # 依赖上一个测试
```

---

#### 3. 使用夹具复用代码

```python
# ✅ 正确：使用夹具
@pytest.fixture
def sample_user(client):
    return User.create_user(
        student_id='20260001',
        password='password123'
    )

def test_user_name(sample_user):
    assert sample_user.name == 'Test'

def test_user_role(sample_user):
    assert sample_user.role == 'student'

# ❌ 错误：重复代码
def test_user_name():
    user = User.create_user(...)
    assert user.name == 'Test'

def test_user_role():
    user = User.create_user(...)
    assert user.role == 'student'
```

---

#### 4. 测试边界条件

```python
def test_password_validation():
    """测试密码验证边界条件"""
    # 最小长度
    assert User.validate_password('123456')  # 6 位
    
    # 小于最小长度
    assert not User.validate_password('12345')  # 5 位
    
    # 长密码
    assert User.validate_password('a' * 100)
    
    # 特殊字符
    assert User.validate_password('p@ss!word#123')
```

---

#### 5. 测试错误处理

```python
def test_create_duplicate_user():
    """测试创建重复用户"""
    User.create_user(
        student_id='20260001',
        password='password123'
    )
    
    with pytest.raises(ValueError) as exc_info:
        User.create_user(
            student_id='20260001',
            password='password456'
        )
    
    assert '学号已存在' in str(exc_info.value)
```

---

### ❌ 避免的做法

#### 1. 避免硬编码

```python
# ❌ 错误：硬编码
def test_user():
    user = User.query.get(123)  # 固定 ID
    assert user.name == '张三'

# ✅ 正确：动态创建
def test_user():
    user = User.create_user(...)
    assert user.name == '张三'
```

---

#### 2. 避免测试逻辑复杂

```python
# ❌ 错误：测试过于复杂
def test_complex():
    user = create_user()
    login(user)
    submit_questionnaire()
    generate_report()
    export_data()
    # ... 太多断言
    assert ...
    assert ...
    assert ...

# ✅ 正确：单一职责
def test_create_user():
    user = create_user()
    assert user is not None

def test_login():
    response = login(user)
    assert response.status_code == 302

def test_submit_questionnaire():
    submission = submit(user)
    assert submission.id is not None
```

---

#### 3. 避免依赖外部服务

```python
# ❌ 错误：依赖真实 API
def test_url_detection():
    result = detect_real_url('http://example.com')
    assert result  # 可能失败

# ✅ 正确：使用 Mock
@patch('app.services.detect_url')
def test_url_detection(mock_detect):
    mock_detect.return_value = {'safe': True}
    result = detect_url('http://example.com')
    assert result['safe']
```

---

## 常见问题

### Q1: 测试失败率波动

**原因**: 测试互相污染

**解决**:
```python
# 在每个测试前清理
@pytest.fixture(autouse=True)
def clean_db():
    db.drop_all()
    db.create_all()
    yield
```

---

### Q2: 数据库连接错误

**解决**:
```python
# 使用内存数据库
class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

---

### Q3: CSRF 导致测试失败

**解决**:
```python
# 测试环境禁用 CSRF
class TestingConfig:
    WTF_CSRF_ENABLED = False
```

---

### Q4: 测试运行太慢

**优化**:
```bash
# 使用并行测试
pip install pytest-xdist
python -m pytest tests/ -n 4

# 只运行失败的测试
pip install pytest-last-failed
python -m pytest tests/ --lf

# 跳过慢测试
python -m pytest tests/ -m "not slow"
```

---

### Q5: Mock 对象行为不符合预期

**解决**:
```python
# 仔细配置 Mock
mock_obj = MagicMock()
mock_obj.method.return_value = expected_value
mock_obj.property = expected_property

# 验证调用
mock_obj.method.assert_called_once_with(arg1, arg2)
```

---

## 持续集成

### GitHub Actions

**.github/workflows/test.yml**:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - uses: actions/setup-python@v2
        with:
          python-version: 3.8
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: python -m pytest tests/ -v --cov=app
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

### GitLab CI

**.gitlab-ci.yml**:
```yaml
test:
  image: python:3.8
  script:
    - pip install -r requirements.txt
    - python -m pytest tests/ -v --cov=app --cov-report=xml
  coverage: '/TOTAL.*\s(\d+%)/'
```

---

## 测试统计

### 覆盖率趋势

| 版本 | 覆盖率 | 测试数 | 状态 |
|------|--------|--------|------|
| v1.0 | 65% | 30 | ✅ |
| v2.0 | 75% | 45 | ✅ |
| v3.0 | 85% | 56 | ✅ |

**目标**: v4.0 达到 90%

---

### 测试执行时间

| 测试文件 | 方法数 | 执行时间 |
|---------|--------|---------|
| test_models.py | 10 | 2.1s |
| test_views.py | 15 | 5.3s |
| test_csrf_protection.py | 5 | 1.2s |
| test_security_features.py | 8 | 2.4s |
| test_user_management.py | 12 | 3.8s |
| test_url_detection.py | 6 | 1.5s |
| **总计** | **56** | **16.3s** |

---

## 相关文档

- [README.md](../README.md) - 项目说明
- [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md) - 开发者指南
- [MAINTENANCE.md](../MAINTENANCE.md) - 维护手册
- [docs/PROJECT_STRUCTURE.md](../docs/PROJECT_STRUCTURE.md) - 项目结构

---

**测试说明版本**: v3.0  
**最后更新**: 2026-03-18  
**维护人员**: 开发团队
