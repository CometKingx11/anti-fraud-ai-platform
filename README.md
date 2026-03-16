# Flask 反诈风险评估系统

一个基于 Flask 的大学生反诈风险评估 Web 应用系统。

## 功能特点

- 🎓 大学生反诈风险评估问卷
- 📊 AI 智能分析评估结果
- 📈 多维度风险评估（认知、行为、经历）
- 📄 PDF 报告导出
- 🔐 用户认证与权限管理
- 👨‍💼 管理员仪表板

## 技术栈

- **后端框架**: Flask 2.3.3
- **数据库**: SQLite + SQLAlchemy
- **ORM**: Flask-SQLAlchemy
- **用户认证**: Flask-Login
- **数据库迁移**: Flask-Migrate
- **AI 服务**: DashScope (通义千问)
- **PDF 生成**: ReportLab

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db.py
```

这将创建数据库表并添加测试账户：
- **管理员账户**: 学号 `12345678`, 密码 `admin123`
- **学生账户**: 学号 `87654321`, 密码 `student123`

### 3. 配置环境变量

编辑 `.env` 文件，配置必要的环境变量：

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///anti_fraud.db
UPLOAD_FOLDER=uploads
DASHSCOPE_API_KEY=your-dashscope-api-key-here
FLASK_ENV=development
```

### 4. 运行服务器

```bash
python run.py
```

应用将在以下地址启动：
- http://127.0.0.1:5000
- http://localhost:5000

## 项目结构

```
flask_anti_project/
├── app/                      # 应用主目录
│   ├── models/              # 数据模型
│   │   ├── user.py         # 用户模型
│   │   └── submission.py   # 提交记录模型
│   ├── services/           # 业务服务层
│   │   ├── assessment_service.py    # 评估服务
│   │   ├── ai_analysis_service.py   # AI 分析服务
│   │   └── pdf_service.py          # PDF 生成服务
│   ├── views/              # 视图控制器
│   │   ├── auth_views.py   # 认证视图
│   │   ├── questionnaire_views.py  # 问卷视图
│   │   ├── report_views.py # 报告视图
│   │   └── admin_views.py  # 管理员视图
│   ├── utils/              # 工具函数
│   │   └── helpers.py
│   ├── templates/          # HTML 模板
│   └── __init__.py         # 应用初始化
├── config/                 # 配置文件
│   └── settings.py
├── tests/                  # 测试文件
├── uploads/                # 上传文件目录
├── migrations/             # 数据库迁移文件
├── .env                    # 环境变量配置
├── requirements.txt        # Python 依赖
├── run.py                  # 应用启动文件
└── init_db.py              # 数据库初始化脚本
```

## 主要功能模块

### 1. 用户认证模块
- 学号登录/登出
- 会话管理
- 权限控制

### 2. 问卷调查模块
- 28 道选择题（认知 10 题 + 行为 10 题 + 经历 8 题）
- 2 道开放性问答题
- 支持图片上传（最多 3 张）

### 3. 风险评估模块
- 三维度评分系统：
  - 认知维度（0-40 分）：越高越安全
  - 行为维度（0-40 分）：越高风险越大
  - 经历维度（0-20 分）：越高风险越大
- 基础分数计算（0-100 分）
- AI 智能分析（0-130 分最终得分）

### 4. AI 分析模块
- 集成通义千问大模型
- 综合分析问卷答案和上传图片
- 生成个性化风险点、分析和建议
- 备用规则分析方案（无 API key 时）

### 5. 报告生成模块
- 在线查看评估报告
- PDF 格式导出
- 包含详细分析和建议

### 6. 管理员功能
- 查看所有用户提交记录
- 数据统计与分析

## API 配置

### DashScope API
如需使用 AI 分析功能，需要在 `.env` 文件中配置 DashScope API 密钥：

```env
DASHSCOPE_API_KEY=your-api-key-here
```

如果没有配置 API 密钥，系统将使用基于规则的简单分析。

## 开发环境

- Python 3.8+
- Flask 2.3.3
- Windows / Linux / macOS

## 使用说明

### 学生用户
1. 访问 http://localhost:5000
2. 使用学号和密码登录
3. 填写反诈风险评估问卷
4. 可选择上传图片（聊天记录等）
5. 提交后查看 AI 分析报告
6. 可下载 PDF 版本报告

### 管理员
1. 访问 http://localhost:5000/auth/login
2. 使用管理员账户登录
3. 访问 /admin 查看所有提交记录
4. 统计分析数据

## 注意事项

1. 首次运行前必须执行 `python init_db.py` 初始化数据库
2. 确保 `uploads` 目录存在且有写权限
3. 生产环境应设置更强的 `SECRET_KEY`
4. 生产环境应使用更安全的数据库（如 PostgreSQL）
5. 建议开启 HTTPS 保护用户数据

## 常见问题

### Q: 无法启动服务器？
A: 检查端口是否被占用，可以修改 `.env` 中的 `PORT` 环境变量

### Q: AI 分析不工作？
A: 检查是否正确配置了 `DASHSCOPE_API_KEY`

### Q: 上传图片失败？
A: 检查 `uploads` 目录是否存在且有写权限

## 许可证

本项目仅供学习和研究使用

## 联系方式

如有问题或建议，请联系开发者。
