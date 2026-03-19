# 基于大模型的大学生反诈风险多模态智能评估平台

## 📖 项目说明文档

**版本**: v3.0  
**最后更新**: 2026-03-18  
**开发环境**: Python 3.8+ / Flask 2.3.3

---

## 📋 目录

1. [项目简介](#项目简介)
2. [技术架构](#技术架构)
3. [核心功能](#核心功能)
4. [项目结构](#项目结构)
5. [安装与配置](#安装与配置)
6. [使用说明](#使用说明)
7. [关键代码说明](#关键代码说明)
8. [API 集成](#api 集成)
9. [数据库设计](#数据库设计)
10. [安全特性](#安全特性)
11. [测试说明](#测试说明)
12. [部署指南](#部署指南)
13. [常见问题](#常见问题)

---

## 项目简介

### 背景

随着电信网络诈骗案件频发，大学生群体成为诈骗分子的主要目标。本项目基于大模型技术，构建了一个多模态智能评估平台，用于评估大学生的反诈风险认知水平，并提供针对性的安全教育。

### 目标

- 🎯 评估大学生的反诈风险认知水平
- 📊 提供多维度的风险评估报告
- 🎓 为高校安全教育提供数据支持
- 🔒 保护学生隐私，确保数据安全

### 主要特点

- ✅ 基于 Flask 的 MVC 架构，模块化设计
- ✅ 集成通义千问大模型进行智能分析
- ✅ 支持多模态数据评估（认知、行为、经历）
- ✅ 完善的安全机制（CSRF 保护、密码加密）
- ✅ 响应式设计，支持多终端访问

---

## 技术架构

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Flask | 2.3.3 | Web 框架 |
| Flask-SQLAlchemy | 3.0.5 | ORM 框架 |
| Flask-Login | 0.6.3 | 用户认证 |
| Flask-Migrate | 4.0.5 | 数据库迁移 |
| Flask-WTF | 1.2.1 | 表单处理和 CSRF 保护 |
| Werkzeug | 2.3.7 | WSGI 工具库 |
| dashscope | 1.14.1 | 通义千问 API |
| reportlab | 4.0.4 | PDF 生成 |
| python-dotenv | 1.0.0 | 环境变量管理 |

### 前端技术栈

| 技术 | 用途 |
|------|------|
| Bootstrap 5.3.3 | UI 框架 |
| Font Awesome 6.4.0 | 图标库 |
| ECharts 5.4.3 | 数据可视化 |
| Jinja2 | 模板引擎 |

### 第三方 API

| API | 用途 | 额度 |
|-----|------|------|
| 通义千问 | AI 智能分析 | 按量计费 |
| 360 开放平台 | URL 安全检测 | 1000 次/日 |
| 腾讯电脑管家 | URL 安全检测 | 5000 次/日 |

---

## 核心功能

### 1. 用户管理 👥

**功能模块**: `app/views/admin_views.py`

**主要功能**:
- ✅ 用户 CRUD（创建、查询、更新、删除）
- ✅ 批量导入用户（Excel/CSV）
- ✅ 角色权限管理（学生、教师、管理员）
- ✅ 密码管理（重置、设置）
- ✅ 用户状态管理（启用/禁用）

**关键代码**:
```python
# 创建用户
User.create_user(
    student_id='20260001',
    password='password123',
    role='student',
    name='张三'
)

# 重置密码为固定值
User.reset_password(student_id, '12345678')
```

---

### 2. 风险链接检测 🔗

**功能模块**: `app/services/url_security_service.py`

**主要功能**:
- ✅ 多 API 检测（360、腾讯）
- ✅ 智能降级策略
- ✅ AI 大模型兜底分析
- ✅ 风险评分计算

**检测流程**:
```
用户提交 URL
    ↓
360 API 检测
    ↓ (失败)
腾讯 API 检测
    ↓ (失败)
通义千问 AI 分析
    ↓
返回风险评分
```

---

### 3. 动态问卷系统 📝

**功能模块**: `app/views/questionnaire_views.py`

**主要功能**:
- ✅ 动态配置问卷题目
- ✅ 多维度评分（认知、行为、经历）
- ✅ 实时计算风险等级
- ✅ 自动保存提交记录

**评分维度**:
- **认知维度** (40 分): 反诈知识掌握程度
- **行为维度** (30 分): 日常行为习惯
- **经历维度** (30 分): 受骗经历分析

---

### 4. 风险评估报告 📊

**功能模块**: `app/views/report_views.py`

**主要功能**:
- ✅ 可视化风险图表
- ✅ 多维度分析
- ✅ 历史趋势对比
- ✅ PDF 报告导出

**风险等级**:
- 🟢 低风险 (0-60 分)
- 🟡 中风险 (61-100 分)
- 🟠 高风险 (101-140 分)
- 🔴 极高风险 (141 分以上)

---

### 5. AI 智能分析 🤖

**功能模块**: `app/services/ai_analysis_service.py`

**主要功能**:
- ✅ 多模态数据分析
- ✅ 个性化建议生成
- ✅ 风险趋势预测
- ✅ 智能问答

**AI 分析示例**:
```python
from app.services.ai_analysis_service import AIAnalysisService

service = AIAnalysisService()
analysis = service.analyze_risk(
    cognitive_score=22,
    behavior_score=20,
    experience_score=14
)
# 返回：分析报告和建议
```

---

### 6. 数据导出 📤

**功能模块**: `app/services/export_service.py`

**主要功能**:
- ✅ Excel 数据导出
- ✅ PDF 报告生成
- ✅ 批量导出
- ✅ 自定义导出字段

---

## 项目结构

```
flask_anti_project/
├── app/                          # 应用主目录
│   ├── models/                   # 数据模型层
│   │   ├── __init__.py
│   │   ├── user.py              # 用户模型
│   │   ├── submission.py        # 提交记录模型
│   │   └── questionnaire.py     # 问卷模型
│   │
│   ├── views/                    # 视图控制层
│   │   ├── __init__.py
│   │   ├── auth_views.py        # 认证视图
│   │   ├── admin_views.py       # 管理员视图
│   │   ├── questionnaire_views.py  # 问卷视图
│   │   ├── report_views.py      # 报告视图
│   │   └── questionnaire_mgmt_views.py  # 问卷管理视图
│   │
│   ├── services/                 # 业务服务层
│   │   ├── __init__.py
│   │   ├── ai_analysis_service.py  # AI 分析服务
│   │   ├── assessment_service.py   # 评估服务
│   │   ├── url_security_service.py # URL 检测服务
│   │   ├── export_service.py       # 导出服务
│   │   ├── pdf_service.py          # PDF 生成服务
│   │   └── batch_import_service.py # 批量导入服务
│   │
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   ├── decorators.py        # 装饰器（权限控制）
│   │   └── helpers.py           # 辅助函数
│   │
│   ├── templates/                # HTML 模板
│   │   ├── base.html            # 基础模板
│   │   ├── admin/               # 管理员页面
│   │   ├── auth/                # 认证页面
│   │   ├── questionnaire/       # 问卷页面
│   │   └── reports/             # 报告页面
│   │
│   └── __init__.py              # 应用工厂
│
├── config/                       # 配置文件
│   └── settings.py              # 环境配置
│
├── scripts/                      # 脚本工具
│   ├── init_db.py               # 初始化数据库
│   ├── migrate_db.py            # 数据库迁移
│   ├── clean_db.py              # 清空数据库
│   └── ...
│
├── tests/                        # 测试文件
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_csrf_protection.py
│   └── ...
│
├── docs/                         # 项目文档
│   ├── features/                # 功能文档
│   ├── guides/                  # 使用指南
│   └── PROJECT_STRUCTURE.md     # 项目结构说明
│
├── examples/                     # 示例文件
│   └── users_import_example.csv
│
├── instance/                     # 实例文件
│   └── anti_fraud_dev.db
│
├── uploads/                      # 上传文件
│
├── .env                          # 环境变量
├── .env.example                  # 环境变量示例
├── requirements.txt              # 依赖配置
├── run.py                        # 启动脚本
└── README.md                     # 项目说明
```

---

## 安装与配置

### 1. 环境要求

- Python 3.8+
- pip 包管理器
- Git

### 2. 克隆项目

```bash
git clone <项目地址>
cd flask_anti_project
```

### 3. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 安全密钥
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=sqlite:///anti_fraud_dev.db

# DashScope API 密钥
DASHSCOPE_API_KEY=your-dashscope-api-key

# 上传文件配置
UPLOAD_FOLDER=uploads

# 运行环境
FLASK_ENV=development
```

### 6. 初始化数据库

```bash
python scripts/init_db.py
```

### 7. 启动应用

```bash
python run.py
```

访问：`http://127.0.0.1:5000`

---

## 使用说明

### 管理员快速开始

#### 1. 登录管理员账号

- 学号：`88888888`
- 密码：`admin123`

#### 2. 创建用户

1. 进入"用户管理"
2. 点击"创建用户"
3. 填写信息（学号、姓名、角色、密码）
4. 点击"创建"

#### 3. 批量导入用户

1. 准备 Excel 文件（格式参考 `examples/users_import_example.csv`）
2. 进入"用户管理" → "批量导入"
3. 上传文件
4. 确认导入

#### 4. 配置问卷

1. 进入"问卷管理"
2. 添加/编辑问题
3. 配置分值和选项
4. 保存配置

#### 5. 查看报告

1. 进入"仪表板"
2. 查看整体数据
3. 查看用户详情
4. 导出报告

---

### 学生使用流程

#### 1. 登录

- 使用管理员分配的学号和密码登录

#### 2. 填写问卷

1. 进入"风险评估"
2. 回答所有问题
3. 提交问卷

#### 3. 查看报告

1. 提交后自动跳转
2. 查看风险评分
3. 查看详细分析
4. 下载 PDF 报告

---

## 关键代码说明

### 1. 应用工厂 (`app/__init__.py`)

```python
def create_app(config_class=Config):
    """
    应用工厂函数
    创建并配置 Flask 应用实例
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # 注入 CSRF token
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=lambda: generate_csrf())
    
    # 注册蓝图
    register_blueprints(app)
    
    return app
```

**说明**:
- 使用工厂模式创建应用实例
- 支持多环境配置
- 模块化设计，易于维护

---

### 2. 用户模型 (`app/models/user.py`)

```python
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='student')
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """密码加密"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """密码验证"""
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def create_user(cls, student_id, password, role='student', name=None):
        """创建用户"""
        user = cls(student_id=student_id, name=name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
```

**说明**:
- 继承 Flask-Login 的 UserMixin
- 密码加密存储
- 提供便捷的 CRUD 方法

---

### 3. URL 检测服务 (`app/services/url_security_service.py`)

```python
class URLSecurityService:
    def detect_url(self, url):
        """
        检测 URL 安全性
        使用降级策略：360 API → 腾讯 API → AI 分析
        """
        # 尝试 360 API
        try:
            result = self._detect_by_360(url)
            if result:
                return result
        except Exception:
            pass
        
        # 尝试腾讯 API
        try:
            result = self._detect_by_tencent(url)
            if result:
                return result
        except Exception:
            pass
        
        # 使用 AI 分析兜底
        return self._detect_by_ai(url)
```

**说明**:
- 智能降级策略
- 确保服务可用性
- AI 大模型兜底

---

### 4. 权限装饰器 (`app/utils/decorators.py`)

```python
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(role):
    """
    角色权限装饰器
    限制只有特定角色的用户可以访问
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if current_user.role != role:
                flash('权限不足', 'danger')
                return redirect(url_for('questionnaire.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

**说明**:
- 基于角色的访问控制
- 自动重定向未授权用户
- 可复用，易于维护

---

## API 集成

### 1. 通义千问 API

**配置**:
```python
import dashscope

dashscope.api_key = os.environ.get('DASHSCOPE_API_KEY')

response = dashscope.Generation.call(
    model='qwen-turbo',
    prompt='请分析这个反诈风险评分：...'
)
```

**用途**:
- 多模态数据分析
- 智能建议生成
- 风险趋势预测

---

### 2. 360 开放平台 API

**配置**:
```python
import requests

def detect_by_360(url):
    api_url = 'https://openapi.360.cn/urlcheck.json'
    params = {
        'appkey': 'your-appkey',
        'url': url
    }
    response = requests.get(api_url, params=params)
    return response.json()
```

**用途**:
- URL 安全性检测
- 恶意网站识别

---

### 3. 腾讯电脑管家 API

**配置**:
```python
def detect_by_tencent(url):
    api_url = 'https://openapi.guanjia.qq.com/scan'
    params = {
        'key': 'your-key',
        'url': url
    }
    response = requests.get(api_url, params=params)
    return response.json()
```

**用途**:
- URL 安全性检测
- 钓鱼网站识别

---

## 数据库设计

### 1. 用户表 (users)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| student_id | VARCHAR(20) | 学号（唯一） |
| password_hash | VARCHAR(255) | 密码哈希 |
| name | VARCHAR(50) | 姓名 |
| role | VARCHAR(20) | 角色 |
| is_active | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

---

### 2. 提交记录表 (submissions)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户 ID（外键） |
| total_score | INTEGER | 总分 |
| cognitive_score | INTEGER | 认知得分 |
| behavior_score | INTEGER | 行为得分 |
| experience_score | INTEGER | 经历得分 |
| risk_level | VARCHAR(20) | 风险等级 |
| answers | TEXT | 答案（JSON） |
| submitted_at | DATETIME | 提交时间 |

---

### 3. 问卷问题表 (questionnaire_questions)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| question_text | TEXT | 问题内容 |
| question_type | VARCHAR(20) | 问题类型 |
| options | TEXT | 选项（JSON） |
| scores | TEXT | 分值（JSON） |
| dimension | VARCHAR(20) | 维度 |
| is_active | BOOLEAN | 是否启用 |

---

## 安全特性

### 1. CSRF 保护

```python
# 所有表单自动包含 CSRF token
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
</form>
```

**特点**:
- 全局启用
- 自动注入 token
- 1 小时有效期

---

### 2. 密码加密

```python
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

**特点**:
- 使用 Werkzeug 的密码哈希
- 不可逆加密
- 防止彩虹表攻击

---

### 3. 会话安全

```python
# 配置
SESSION_COOKIE_HTTPONLY = True  # 防止 XSS
SESSION_COOKIE_SAMESITE = 'Lax'  # 防止 CSRF
PERMANENT_SESSION_LIFETIME = 3600  # 1 小时过期
```

**特点**:
- HttpOnly Cookie
- SameSite 保护
- 会话超时机制

---

### 4. 权限控制

```python
@role_required('admin')
def admin_dashboard():
    """只有管理员可以访问"""
    pass
```

**特点**:
- 基于角色的访问控制
- 自动验证权限
- 未授权自动重定向

---

## 测试说明

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行单个测试文件
python -m pytest tests/test_models.py -v

# 生成覆盖率报告
python -m pytest tests/ --cov=app --cov-report=html
```

### 测试分类

| 测试文件 | 测试内容 |
|---------|---------|
| test_models.py | 数据模型测试 |
| test_views.py | 视图函数测试 |
| test_csrf_protection.py | CSRF 保护测试 |
| test_security_features.py | 安全功能测试 |
| test_user_management.py | 用户管理测试 |
| test_url_detection.py | URL 检测测试 |

---

## 部署指南

### 1. 生产环境配置

编辑 `.env`:

```env
FLASK_ENV=production
SECRET_KEY=<强随机密钥>
DATABASE_URL=postgresql://user:password@localhost/dbname
DASHSCOPE_API_KEY=<你的 API 密钥>
```

---

### 2. 使用 Gunicorn

```bash
# 安装
pip install gunicorn

# 启动
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

---

### 3. 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### 4. 使用 Supervisor 管理进程

```ini
[program:flask_anti]
command=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 run:app
directory=/path/to/flask_anti_project
user=www-data
autostart=true
autorestart=true
```

---

## 常见问题

### Q1: 无法启动应用

**解决**:
```bash
# 检查依赖
pip install -r requirements.txt

# 检查环境变量
cat .env

# 查看详细错误
python run.py
```

---

### Q2: 数据库错误

**解决**:
```bash
# 重新初始化数据库
python scripts/clean_db.py
python scripts/init_db.py
```

---

### Q3: CSRF token 无效

**解决**:
1. 清除浏览器缓存（Ctrl + F5）
2. 检查 `app/__init__.py` 中的 CSRF 配置
3. 确认表单包含 CSRF token

---

### Q4: API 调用失败

**解决**:
```bash
# 检查 API 密钥
cat .env | grep DASHSCOPE_API_KEY

# 检查网络连接
ping api.dashscope.cn

# 查看日志
tail -f logs/app.log
```

---

### Q5: 用户上传文件无法访问

**解决**:
```bash
# 检查上传目录权限
chmod -R 755 uploads/

# 检查配置
cat .env | grep UPLOAD_FOLDER
```

---

## 开发团队

- **开发者**: 小土豆 233
- **版本**: v3.0
- **许可证**: MIT

---

## 更新日志

### v3.0 (2026-03-18)
- ✅ 集成通义千问大模型
- ✅ 实现智能降级策略
- ✅ 完善 CSRF 保护
- ✅ 优化项目结构
- ✅ 添加完整文档

### v2.0 (2026-03-10)
- ✅ 添加动态问卷系统
- ✅ 实现多维度评分
- ✅ 添加 PDF 报告导出

### v1.0 (2026-03-01)
- ✅ 初始版本发布
- ✅ 基础用户管理
- ✅ 简单风险评估

---

## 联系方式

- **邮箱**: support@example.com
- **GitHub**: https://github.com/your-repo
- **文档**: https://your-docs.com

---

**最后更新**: 2026-03-18  
**文档版本**: v3.0
