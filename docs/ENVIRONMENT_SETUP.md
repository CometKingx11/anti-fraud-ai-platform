# 环境配置说明文档

**版本**: v3.0  
**最后更新**: 2026-03-25  
**适用环境**: 开发环境 / 生产环境

---

## 📋 目录

1. [配置文件说明](#配置文件说明)
2. [必需环境变量](#必需环境变量)
3. [可选环境变量](#可选环境变量)
4. [开发环境配置](#开发环境配置)
5. [生产环境配置](#生产环境配置)
6. [配置示例](#配置示例)
7. [常见问题](#常见问题)

---

## 配置文件说明

### .env 文件位置

项目根目录下的 `.env` 文件是主要的环境配置文件，包含所有敏感配置信息。

```
flask_anti_project/
├── .env              # 主配置文件（需手动创建）
├── .env.example      # 配置文件模板（仅供参考）
└── config/
    └── settings.py   # 配置加载逻辑
```

### ⚠️ 重要提示

1. **不要将 `.env` 文件提交到 Git** - 已添加到 `.gitignore`
2. **生产环境使用独立的密钥** - 不要使用开发环境的密钥
3. **定期更换密码和密钥** - 建议每季度更换一次

---

## 必需环境变量

以下配置项是系统运行所必需的，必须在 `.env` 文件中配置：

### 1. SECRET_KEY

**用途**: Flask 应用密钥，用于加密 Session、CSRF Token 等安全相关功能

**要求**: 
- 开发环境：至少 16 字节
- 生产环境：**必须使用 32 字节以上的强随机字符串**

**生成方法**:
```python
# Python 生成随机密钥
import secrets
print(secrets.token_hex(32))  # 生成 64 字符的十六进制字符串
```

**示例**:
```env
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

**未配置的后果**: 应用无法启动或存在严重安全风险

---

### 2. DATABASE_URL

**用途**: 数据库连接字符串

**支持类型**: SQLite, MySQL, PostgreSQL

**默认值**: `sqlite:///anti_fraud.db`

**格式说明**:
```
# SQLite (推荐用于开发和小型部署)
sqlite:///相对路径/数据库名.db
sqlite:////绝对路径/数据库名.db

# MySQL
mysql+pymysql://用户名：密码@主机：端口/数据库名

# PostgreSQL
postgresql://用户名：密码@主机：端口/数据库名
```

**示例**:
```env
# 开发环境 - SQLite
DATABASE_URL=sqlite:///anti_fraud_dev.db

# 生产环境 - MySQL
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/anti_fraud_prod
```

**注意**: 
- 首次使用前需要运行初始化脚本创建数据库表
- 生产环境建议使用 MySQL 或 PostgreSQL

---

### 3. DASHSCOPE_API_KEY

**用途**: 通义千问大模型 API 密钥，用于 AI 智能分析功能

**获取方式**: 
1. 访问 https://dashscope.console.aliyun.com/
2. 注册阿里云账号
3. 开通 DashScope 服务
4. 创建 API Key

**免费额度**: 按量计费，新用户有一定免费额度

**示例**:
```env
DASHSCOPE_API_KEY=sk-eddacc4bfb5b451984bafe111d2b6846
```

**未配置的后果**: AI 分析功能不可用，但其他功能正常

---

## 可选环境变量

以下配置项有合理的默认值，可根据需要选择是否配置：

### 邮件服务配置

用于发送风险预警邮件、欢迎邮件等功能。

#### MAIL_SERVER

**用途**: SMTP 邮件服务器地址

**默认值**: `smtp.qq.com` (QQ 邮箱)

**常见邮件服务器**:
- QQ 邮箱：`smtp.qq.com`
- 163 邮箱：`smtp.163.com`
- Gmail: `smtp.gmail.com`
- Outlook: `smtp-mail.outlook.com`

**示例**:
```env
MAIL_SERVER=smtp.qq.com
```

---

#### MAIL_PORT

**用途**: SMTP 服务器端口

**默认值**: `465` (SSL 加密端口)

**可选值**:
- `465` - SSL 加密（推荐）
- `587` - TLS 加密
- `25` - 非加密（不推荐）

**示例**:
```env
MAIL_PORT=465
```

---

#### MAIL_USE_SSL

**用途**: 是否启用 SSL 加密

**默认值**: `True`

**可选值**: `True` 或 `False`

**示例**:
```env
MAIL_USE_SSL=True
```

---

#### MAIL_USE_TLS

**用途**: 是否启用 TLS 加密

**默认值**: `False`

**重要**: 如果使用 QQ 邮箱，**必须设置为 False**，否则会报错

**示例**:
```env
MAIL_USE_TLS=False
```

---

#### MAIL_USERNAME

**用途**: 发送邮件的邮箱账号

**默认值**: 无（必须手动配置）

**示例**:
```env
MAIL_USERNAME=your-qq-email@qq.com
```

---

#### MAIL_PASSWORD

**用途**: SMTP 授权码（不是邮箱登录密码！）

**获取方式** (以 QQ 邮箱为例):
1. 登录邮箱网页版
2. 进入"设置" -> "账户"
3. 开启"POP3/SMTP/IMAP 服务"
4. 生成授权码（16 位字符串）

**示例**:
```env
MAIL_PASSWORD=abcdefghijklmnop
```

**注意**: 
- 这是授权码，不是邮箱登录密码
- 每个邮箱服务商的获取方式不同

---

### API 密钥配置

#### VIRUSTOTAL_API_KEY

**用途**: VirusTotal URL 安全检测 API 密钥

**获取方式**: 
1. 访问 https://www.virustotal.com/
2. 注册账号
3. 在个人中心获取 API Key

**免费额度**: 每分钟 4 次请求

**示例**:
```env
VIRUSTOTAL_API_KEY=your-virustotal-api-key
```

**未配置的后果**: URL 检测功能将使用备用方案（腾讯 API 或 AI 分析）

---

### 其他配置项

#### UPLOAD_FOLDER

**用途**: 上传文件存储目录

**默认值**: `uploads`

**示例**:
```env
UPLOAD_FOLDER=uploads
```

**注意**: 目录会自动创建，确保应用有写入权限

---

#### LOG_LEVEL

**用途**: 日志级别

**可选值**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

**默认值**: `INFO`

**建议**:
- 开发环境：`DEBUG`
- 生产环境：`WARNING` 或 `ERROR`

**示例**:
```env
LOG_LEVEL=DEBUG
```

---

#### FLASK_ENV

**用途**: Flask 运行环境

**可选值**: `development`, `production`, `testing`

**默认值**: `development`

**示例**:
```env
FLASK_ENV=development
```

---

#### DEV_DATABASE_URL

**用途**: 开发环境专用数据库 URL

**默认值**: 同 `DATABASE_URL`

**用途说明**: 当需要区分开发和生产数据库时使用

**示例**:
```env
DEV_DATABASE_URL=sqlite:///anti_fraud_dev.db
DATABASE_URL=sqlite:///anti_fraud_prod.db
```

---

## 开发环境配置

### 最小化配置（快速开始）

如果只想快速启动项目进行开发，只需配置以下 3 个变量：

```env
# 1. 应用密钥（开发环境可用简单密钥）
SECRET_KEY=dev-secret-key-123456

# 2. 数据库配置
DATABASE_URL=sqlite:///anti_fraud_dev.db

# 3. AI 分析 API（可选，但不配置则 AI 功能不可用）
DASHSCOPE_API_KEY=sk-your-api-key
```

### 完整开发环境配置

```env
# 基础配置
SECRET_KEY=dev-secret-key-for-development-only
DATABASE_URL=sqlite:///anti_fraud_dev.db
DEV_DATABASE_URL=sqlite:///anti_fraud_dev.db
FLASK_ENV=development
LOG_LEVEL=DEBUG

# AI 服务配置
DASHSCOPE_API_KEY=sk-your-dashscope-api-key
VIRUSTOTAL_API_KEY=your-virustotal-api-key

# 邮件服务配置（用于测试邮件功能）
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=your-test-qq-email@qq.com
MAIL_PASSWORD=your-smtp-auth-code

# 文件上传配置
UPLOAD_FOLDER=uploads
```

---

## 生产环境配置

### 安全要求

1. **SECRET_KEY**: 必须使用 32 字节以上的强随机字符串
2. **数据库**: 建议使用 MySQL 或 PostgreSQL
3. **邮件配置**: 必须配置才能发送风险预警邮件
4. **API 密钥**: 所有第三方 API 密钥都必须配置

### 生产环境配置示例

```env
# ===== 安全配置 =====
# 使用 Python 生成：import secrets; print(secrets.token_hex(32))
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6

# ===== 数据库配置 =====
# 生产环境强烈建议使用 MySQL 或 PostgreSQL
DATABASE_URL=mysql+pymysql://prod_user:strong_password@localhost:3306/anti_fraud_prod?charset=utf8mb4

# ===== 环境配置 =====
FLASK_ENV=production
LOG_LEVEL=WARNING

# ===== AI 服务配置 =====
DASHSCOPE_API_KEY=sk-prod-api-key-here
VIRUSTOTAL_API_KEY=prod-virustotal-api-key

# ===== 邮件服务配置 =====
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=official-email@qq.com
MAIL_PASSWORD=prod-smtp-auth-code

# ===== 文件存储配置 =====
UPLOAD_FOLDER=/var/www/flask_anti_project/uploads

# ===== 时区配置 =====
TIMEZONE=Asia/Shanghai
```

### 生产环境额外配置项

以下配置在生产环境中建议添加：

```env
# 域名配置（如果使用反向代理）
SERVER_NAME=your-domain.com
PREFERRED_URL_SCHEME=https

# 缓存配置（如果使用 Redis）
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis

# 会话过期时间（秒）
PERMANENT_SESSION_LIFETIME=3600

# 最大上传文件大小（MB）
MAX_CONTENT_LENGTH=16
```

---

## 配置示例

### 示例 1: 学生本地开发环境

```env
# 学生个人学习使用，最简单配置
SECRET_KEY=student-dev-key-123456
DATABASE_URL=sqlite:///anti_fraud.db
DASHSCOPE_API_KEY=sk-student-api-key
FLASK_ENV=development
```

**说明**: 仅配置最基本的 3 项，用于本地学习和代码调试

---

### 示例 2: 教师演示环境

```env
# 用于课堂演示，配置邮件功能
SECRET_KEY=demo-secret-key-2026
DATABASE_URL=sqlite:///demo_anti_fraud.db
DASHSCOPE_API_KEY=sk-demo-api-key
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=demo@qq.com
MAIL_PASSWORD=demo-auth-code
FLASK_ENV=development
LOG_LEVEL=INFO
```

**说明**: 添加邮件配置，演示风险预警邮件发送功能

---

### 示例 3: 学校正式部署

```env
# 学校保卫处正式使用，生产环境配置
SECRET_KEY=university-secure-key-very-long-string-at-least-64-chars
DATABASE_URL=mysql+pymysql://db_user:db_password@127.0.0.1:3306/university_anti_fraud?charset=utf8mb4
DASHSCOPE_API_KEY=sk-university-api-key
VIRUSTOTAL_API_KEY=university-vt-key
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=security@university.edu.cn
MAIL_PASSWORD=university-auth-code
FLASK_ENV=production
LOG_LEVEL=WARNING
UPLOAD_FOLDER=/opt/flask_app/uploads
TIMEZONE=Asia/Shanghai
```

**说明**: 完整的生產环境配置，使用 MySQL 数据库，所有功能齐全

---

## 常见问题

### Q1: 配置文件在哪里？

**A**: 在项目根目录下创建 `.env` 文件（没有扩展名），可以直接复制 `.env.example` 修改。

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

---

### Q2: 为什么配置不生效？

**A**: 检查以下几点：
1. 文件名必须是 `.env`（不是 `.env.txt` 或其他）
2. 确保文件在**项目根目录**
3. 重启 Flask 应用（配置在启动时加载）
4. 检查是否有拼写错误

---

### Q3: SECRET_KEY 报警告怎么办？

**A**: 这是安全提示，解决方法：
```python
# 生成一个强随机密钥
import secrets
print(secrets.token_hex(32))
```
将生成的字符串复制到 `.env` 文件的 `SECRET_KEY` 配置项。

---

### Q4: 邮件发送失败，报错"STARTTLS extension not supported"

**A**: 这是 TLS 配置问题，解决方法：
```env
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_PORT=465
```
确保这三个配置项正确，特别是 `MAIL_USE_TLS=False`。

---

### Q5: 如何切换开发环境和生产环境？

**A**: 修改 `FLASK_ENV` 配置：
```env
# 开发环境
FLASK_ENV=development

# 生产环境
FLASK_ENV=production
```
或者通过环境变量设置：
```bash
# Windows
set FLASK_ENV=production

# Linux/Mac
export FLASK_ENV=production
```

---

### Q6: 数据库文件在哪里？

**A**: SQLite 数据库文件位置由 `DATABASE_URL` 决定：
- `sqlite:///anti_fraud.db` - 当前目录
- `sqlite:///instance/anti_fraud.db` - instance 子目录
- 绝对路径 - 指定的完整路径

可以通过以下方式查看实际位置：
```python
from flask import current_app
print(current_app.config['SQLALCHEMY_DATABASE_URI'])
```

---

### Q7: 如何验证配置是否成功？

**A**: 运行以下命令测试：
```bash
python config/settings.py
```
会输出当前配置信息，包括：
- 当前环境
- 调试模式
- 数据库 URL
- 上传目录
- API Key 配置状态

---

### Q8: 多个开发人员如何管理不同的配置？

**A**: 推荐做法：
1. 每人创建自己的 `.env.local` 文件（个人配置）
2. 在 `.gitignore` 中添加 `.env.local`
3. 使用环境变量覆盖：
   ```bash
   export SECRET_KEY=my-personal-key
   python run.py
   ```

---

### Q9: 生产环境如何安全地管理配置？

**A**: 最佳实践：
1. **不要硬编码在代码中**
2. 使用环境变量管理工具（如 Docker Secrets、AWS Secrets Manager）
3. 限制 `.env` 文件的访问权限：
   ```bash
   chmod 600 .env  # 只有所有者可读写
   chown www-data:www-data .env  # 设置正确的所有者
   ```

---

### Q10: 配置文件修改后需要重启吗？

**A**: 
- **开发环境** (FLASK_ENV=development): 是的，需要重启 Flask 应用
- **生产环境**: 必须重启 Gunicorn/uWSGI 等服务

配置在应用启动时加载，运行时修改不会自动生效。

---

## 附录：配置检查清单

在部署前，请确认已完成以下检查：

### 开发环境检查清单
- [ ] SECRET_KEY 已配置（至少 16 字节）
- [ ] DATABASE_URL 已配置
- [ ] DASHSCOPE_API_KEY 已配置（如需 AI 功能）
- [ ] 上传目录有写入权限
- [ ] 数据库文件可创建/访问

### 生产环境检查清单
- [ ] SECRET_KEY 已配置（至少 32 字节强随机字符串）
- [ ] 使用 MySQL 或 PostgreSQL 数据库
- [ ] 数据库用户有适当权限
- [ ] 所有必需的 API Key 已配置
- [ ] 邮件服务已配置并测试
- [ ] 上传目录权限正确
- [ ] FLASK_ENV=production
- [ ] LOG_LEVEL=WARNING 或 ERROR
- [ ] 启用了 HTTPS
- [ ] .env 文件权限设置为 600

---

## 获取帮助

如遇到配置相关问题：
1. 查看本文档的"常见问题"部分
2. 检查应用日志查看详细错误信息
3. 参考项目 README.md 的安装说明
4. 联系项目维护者或技术支持

---

**文档版本**: v1.0  
**维护者**: 脆心柚  
**最后更新**: 2026-03-25
