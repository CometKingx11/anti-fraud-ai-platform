# 项目结构说明

## 📁 目录结构

```
flask_anti_project/
├── app/                          # 应用主目录（MVC 架构）
│   ├── models/                   # 数据模型层
│   │   ├── __init__.py
│   │   ├── submission.py        # 提交记录模型
│   │   └── user.py              # 用户模型
│   ├── views/                    # 视图控制层
│   │   ├── __init__.py
│   │   ├── admin_views.py       # 管理员视图
│   │   ├── auth_views.py        # 认证视图
│   │   ├── questionnaire_views.py  # 问卷视图
│   │   ├── report_views.py      # 报告视图
│   │   └── questionnaire_mgmt_views.py  # 问卷管理视图
│   ├── services/                 # 业务服务层
│   │   ├── __init__.py
│   │   ├── ai_analysis_service.py  # AI 分析服务
│   │   ├── assessment_service.py   # 评估服务
│   │   ├── export_service.py       # 导出服务
│   │   └── pdf_service.py          # PDF 生成服务
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   ├── decorators.py        # 装饰器
│   │   └── helpers.py           # 辅助函数
│   ├── templates/                # HTML 模板
│   │   ├── base.html            # 基础模板
│   │   ├── admin/               # 管理员页面
│   │   ├── auth/                # 认证页面
│   │   ├── questionnaire/       # 问卷页面
│   │   └── reports/             # 报告页面
│   └── __init__.py              # 应用工厂
│
├── config/                       # 配置文件
│   └── settings.py              # 配置类
│
├── scripts/                      # 数据库脚本工具
│   ├── add_questions_direct.py  # 直接添加问题
│   ├── add_questions_manual.py  # 手动添加问题
│   ├── clean_db.py              # 清空数据库
│   ├── init_db.py               # 初始化数据库
│   ├── init_questionnaire_db.py # 初始化问卷数据库
│   ├── migrate_db.py            # 数据库迁移
│   ├── update_db_schema.py      # 更新数据库模式
│   └── update_submission_model.py  # 更新提交模型
│
├── tests/                        # 正式测试文件
│   ├── test_csrf_protection.py  # CSRF 保护测试
│   ├── test_models.py           # 模型测试
│   ├── test_security_features.py # 安全功能测试
│   ├── test_url_detection.py    # URL 检测测试
│   ├── test_user_management.py  # 用户管理测试
│   └── test_views.py            # 视图测试
│
├── docs/                         # 项目文档
│   ├── features/                # 功能文档
│   │   ├── ECharts 可视化与预警功能实现.md
│   │   ├── v3.0 功能实现总结.md
│   │   ├── 功能完善说明.md
│   │   ├── 安全功能实现总结.md
│   │   ├── 安全认证说明.md
│   │   ├── 用户管理功能实现总结.md
│   │   ├── 用户管理功能说明.md
│   │   └── 风险链接检测功能说明.md
│   └── guides/                  # 使用指南
│       ├── 快速上手 - 用户管理.md
│       └── 快速上手指南.md
│
├── examples/                     # 示例文件
│   └── users_import_example.csv # 用户导入示例
│
├── instance/                     # 实例文件
│   └── anti_fraud_dev.db        # 开发数据库
│
├── uploads/                      # 上传文件目录
│   └── [上传的图片文件]
│
├── migrations/                   # 数据库迁移文件（自动生成）
│
├── .env                          # 环境变量配置（敏感信息，勿提交）
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git 忽略配置
├── requirements.txt              # Python 依赖
├── run.py                        # 启动脚本
├── README.md                     # 项目说明
└── 项目需求书.pdf                # 项目需求文档
```

---

## 📂 目录说明

### 核心目录

#### `app/` - 应用主目录
采用 MVC（Model-View-Controller）架构：
- **models/** - 数据模型层，定义数据库表结构
- **views/** - 视图控制层，处理 URL 路由和业务逻辑
- **services/** - 业务服务层，封装复杂业务逻辑
- **utils/** - 工具函数，提供通用辅助功能
- **templates/** - HTML 模板，前端页面

#### `config/` - 配置文件
- 包含所有配置类（开发、测试、生产环境）
- 数据库连接、密钥、API 密钥等配置

#### `scripts/` - 脚本工具
- 数据库初始化、迁移、清理等维护脚本
- 一次性使用的工具脚本

#### `tests/` - 测试文件
- 正式的单元测试和集成测试
- 使用 `pytest` 或 `unittest` 运行

#### `docs/` - 项目文档
- **features/** - 功能实现文档
- **guides/** - 使用指南和教程
- **requirements/** - 需求文档（如有）

#### `examples/` - 示例文件
- 用户导入示例 CSV
- 其他示例数据

#### `instance/` - 实例文件
- 数据库文件（开发环境）
- 不应提交到版本控制

#### `uploads/` - 上传文件
- 用户上传的图片、文件等
- 不应提交到版本控制

---

## 🗂️ 文件分类

### 核心代码文件

**应用入口**:
- `run.py` - Flask 应用启动文件
- `app/__init__.py` - 应用工厂

**模型**:
- `app/models/user.py` - 用户模型
- `app/models/submission.py` - 提交记录模型

**视图**:
- `app/views/auth_views.py` - 认证相关视图
- `app/views/admin_views.py` - 管理员相关视图
- `app/views/questionnaire_views.py` - 问卷相关视图
- `app/views/report_views.py` - 报告相关视图
- `app/views/questionnaire_mgmt_views.py` - 问卷管理视图

**服务**:
- `app/services/ai_analysis_service.py` - AI 分析服务
- `app/services/assessment_service.py` - 评估服务
- `app/services/export_service.py` - 导出服务
- `app/services/pdf_service.py` - PDF 生成服务

**工具**:
- `app/utils/decorators.py` - 装饰器（权限控制等）
- `app/utils/helpers.py` - 辅助函数（验证、处理等）

**配置**:
- `config/settings.py` - 配置类

---

### 脚本文件（scripts/）

**数据库初始化**:
- `init_db.py` - 初始化数据库
- `init_questionnaire_db.py` - 初始化问卷数据库

**数据库迁移**:
- `migrate_db.py` - 数据库迁移
- `update_db_schema.py` - 更新数据库模式

**数据维护**:
- `clean_db.py` - 清空数据库
- `add_questions_direct.py` - 直接添加问题
- `add_questions_manual.py` - 手动添加问题

**模型更新**:
- `update_submission_model.py` - 更新提交模型

---

### 测试文件（tests/）

**功能测试**:
- `test_models.py` - 测试数据模型
- `test_views.py` - 测试视图函数
- `test_user_management.py` - 测试用户管理

**安全测试**:
- `test_csrf_protection.py` - 测试 CSRF 保护
- `test_security_features.py` - 测试安全功能

**专项测试**:
- `test_url_detection.py` - 测试 URL 检测功能

---

### 文档文件（docs/）

**功能文档（docs/features/）**:
- `v3.0 功能实现总结.md` - V3.0 版本功能总结
- `功能完善说明.md` - 功能完善说明
- `ECharts 可视化与预警功能实现.md` - ECharts 可视化实现
- `安全功能实现总结.md` - 安全功能实现
- `安全认证说明.md` - 安全认证机制
- `用户管理功能实现总结.md` - 用户管理功能实现
- `用户管理功能说明.md` - 用户管理功能说明
- `风险链接检测功能说明.md` - 风险链接检测功能

**使用指南（docs/guides/）**:
- `快速上手指南.md` - 快速上手指南
- `快速上手 - 用户管理.md` - 用户管理使用指南

---

### 配置文件

**环境配置**:
- `.env` - 环境变量（**不要提交到 Git**）
- `.env.example` - 环境变量示例（可以提交）

**项目配置**:
- `requirements.txt` - Python 依赖包
- `.gitignore` - Git 忽略规则

---

### 数据文件

**示例数据**:
- `examples/users_import_example.csv` - 用户导入示例

**数据库**:
- `instance/anti_fraud_dev.db` - 开发数据库（**不要提交到 Git**）

---

## 📌 重要说明

### 不应提交到版本控制的文件

以下文件应在 `.gitignore` 中：

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# 环境变量
.env

# 数据库
instance/*.db
*.sqlite3

# 上传文件
uploads/*
!uploads/.gitkeep

# IDE
.idea/
.vscode/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db
```

---

### 开发流程

1. **开发新功能**:
   ```
   app/
   ├── models/      # 添加新模型
   ├── views/       # 添加新视图
   ├── services/    # 添加新服务
   └── templates/   # 添加新模板
   ```

2. **编写测试**:
   ```
   tests/
   └── test_new_feature.py  # 添加新测试
   ```

3. **更新文档**:
   ```
   docs/
   ├── features/    # 添加功能文档
   └── guides/      # 添加使用指南
   ```

4. **数据库变更**:
   ```
   scripts/
   └── migrate_db.py  # 执行迁移
   ```

---

## 🎯 项目结构优势

1. **清晰的模块化**: 按功能模块划分，易于维护
2. **MVC 架构**: 模型 - 视图 - 控制器分离，职责清晰
3. **服务层封装**: 复杂业务逻辑封装在 services 中
4. **完善的测试**: 每个模块都有对应的测试
5. **详细的文档**: 功能文档、使用指南齐全
6. **易于扩展**: 新增功能只需添加对应文件

---

**整理时间**: 2026-03-18  
**整理版本**: v3.0
