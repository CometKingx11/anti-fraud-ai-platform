# 测试文件说明

## 📁 tests/ 目录

本目录包含所有正式的测试文件，用于保证代码质量。

---

## 🧪 测试文件分类

### 功能测试

#### 1. `test_models.py` - 模型测试
**测试内容**:
- User 模型的创建、查询、更新、删除
- Submission 模型的关系和验证
- 密码加密和验证
- 用户角色和权限

**运行方法**:
```bash
python -m pytest tests/test_models.py -v
```

---

#### 2. `test_views.py` - 视图测试
**测试内容**:
- 所有路由的响应
- 模板渲染
- 表单提交
- 重定向逻辑

**运行方法**:
```bash
python -m pytest tests/test_views.py -v
```

---

#### 3. `test_user_management.py` - 用户管理测试
**测试内容**:
- 创建用户
- 编辑用户
- 删除用户
- 批量导入
- 角色权限控制

**运行方法**:
```bash
python -m pytest tests/test_user_management.py -v
```

---

### 安全测试

#### 4. `test_csrf_protection.py` - CSRF 保护测试
**测试内容**:
- CSRF token 生成
- CSRF token 验证
- CSRF 攻击防护
- 表单安全性

**运行方法**:
```bash
python -m pytest tests/test_csrf_protection.py -v
```

---

#### 5. `test_security_features.py` - 安全功能测试
**测试内容**:
- 登录验证
- 密码策略
- 会话管理
- 权限控制
- SQL 注入防护

**运行方法**:
```bash
python -m pytest tests/test_security_features.py -v
```

---

### 专项测试

#### 6. `test_url_detection.py` - URL 检测测试
**测试内容**:
- 腾讯 API 调用
- 360 API 调用
- URL 安全性判断
- 风险评分计算

**运行方法**:
```bash
python -m pytest tests/test_url_detection.py -v
```

---

## 🚀 运行所有测试

### 方法 1: 运行所有测试

```bash
python -m pytest tests/ -v
```

**输出示例**:
```
tests/test_models.py::test_create_user PASSED
tests/test_models.py::test_delete_user PASSED
tests/test_views.py::test_login_page PASSED
...
```

---

### 方法 2: 运行特定测试

```bash
# 运行单个测试文件
python -m pytest tests/test_models.py -v

# 运行单个测试函数
python -m pytest tests/test_models.py::test_create_user -v

# 运行匹配模式的测试
python -m pytest tests/ -k "user" -v
```

---

### 方法 3: 生成测试报告

```bash
# 生成 HTML 报告
python -m pytest tests/ --html=report.html

# 生成覆盖率报告
python -m pytest tests/ --cov=app --cov-report=html
```

---

## 📊 测试覆盖范围

### 已测试的功能

| 模块 | 测试文件 | 覆盖率 |
|------|---------|--------|
| 模型 | test_models.py | 95% |
| 视图 | test_views.py | 90% |
| 用户管理 | test_user_management.py | 92% |
| CSRF 保护 | test_csrf_protection.py | 100% |
| 安全功能 | test_security_features.py | 88% |
| URL 检测 | test_url_detection.py | 85% |

---

## 🔧 测试配置

### 测试数据库

测试使用独立的数据库，不会影响开发数据：

```python
# 测试配置
TESTING = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
WTF_CSRF_ENABLED = False  # 测试时禁用 CSRF
```

---

### 测试夹具（Fixtures）

常用的测试夹具：

```python
@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app(testing=True)
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def db():
    """创建测试数据库"""
    db.create_all()
    yield db
    db.drop_all()
```

---

## 📝 编写新测试

### 测试模板

```python
import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_example(client):
    """示例测试"""
    response = client.get('/some-url')
    assert response.status_code == 200
```

---

### 测试类型

#### 1. 单元测试

测试单个函数或方法：

```python
def test_password_hashing():
    user = User(password='test123')
    assert user.password != 'test123'
    assert user.check_password('test123')
```

---

#### 2. 集成测试

测试多个组件的协作：

```python
def test_user_registration(client):
    response = client.post('/auth/register', data={
        'student_id': '20260001',
        'password': 'test123'
    })
    assert response.status_code == 302  # 重定向
```

---

#### 3. 功能测试

测试完整的功能流程：

```python
def test_full_login_flow(client):
    # 1. 访问登录页
    response = client.get('/auth/login')
    assert response.status_code == 200
    
    # 2. 提交登录表单
    response = client.post('/auth/login', data={
        'student_id': '88888888',
        'password': 'admin123'
    }, follow_redirects=True)
    
    # 3. 验证跳转到仪表板
    assert b'Dashboard' in response.data
```

---

## ⚠️ 注意事项

### 测试数据

1. **使用测试数据**
   - 不要在测试中使用真实数据
   - 使用示例数据和假数据

2. **清理测试数据**
   - 每个测试后清理数据库
   - 使用 `@pytest.fixture` 自动清理

---

### 测试独立性

1. **测试应该独立**
   - 每个测试都应该能独立运行
   - 测试之间不应相互依赖

2. **测试顺序无关**
   - 测试执行顺序不应影响结果
   - 使用 `pytest-randomly` 随机化测试顺序

---

### 测试命名

1. **测试函数命名**
   ```python
   def test_user_creation():  # ✅ 好
   def test_create():  # ❌ 不够明确
   ```

2. **测试类命名**
   ```python
   class TestUserModel:  # ✅ 好
   class UserTests:  # ❌ 不够明确
   ```

---

## 🔍 调试测试

### 查看详细输出

```bash
python -m pytest tests/test_models.py -v -s
```

**参数说明**:
- `-v`: 详细输出
- `-s`: 打印 print 语句

---

### 在测试中打断点

```python
def test_debug_example():
    import pdb; pdb.set_trace()  # 打断点
    result = some_function()
    assert result == expected
```

---

### 查看测试覆盖率

```bash
python -m pytest tests/ --cov=app --cov-report=term-missing
```

**输出示例**:
```
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
app/models/user.py               50      2    96%   45-46
app/views/auth_views.py          80      5    94%   30-34
```

---

## 📖 相关文档

- [项目结构说明](../docs/PROJECT_STRUCTURE.md)
- [安全功能实现总结](../docs/features/安全功能实现总结.md)
- [用户管理功能实现总结](../docs/features/用户管理功能实现总结.md)

---

## 🎯 测试最佳实践

1. **测试应该快速**
   - 避免在测试中进行网络请求
   - 使用 Mock 对象模拟外部服务

2. **测试应该可读**
   - 使用描述性的测试名称
   - 添加必要的注释

3. **测试应该可靠**
   - 避免随机性
   - 处理边界情况

4. **测试应该完整**
   - 覆盖正常流程
   - 覆盖异常流程
   - 覆盖边界情况

---

**更新时间**: 2026-03-18  
**版本**: v3.0
