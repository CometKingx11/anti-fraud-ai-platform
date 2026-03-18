# 脚本工具使用说明

## 📁 scripts/ 目录

本目录包含所有数据库相关的维护和初始化脚本。

---

## 🔧 脚本分类

### 数据库初始化

#### 1. `init_db.py` - 初始化数据库
**用途**: 创建所有数据库表并初始化基础数据

**使用方法**:
```bash
python scripts/init_db.py
```

**功能**:
- 创建所有数据库表
- 创建默认管理员账户（学号：88888888，密码：admin123）
- 初始化基础配置

**注意事项**:
- ⚠️ 仅在首次使用时运行
- ⚠️ 会清空现有数据

---

#### 2. `init_questionnaire_db.py` - 初始化问卷数据库
**用途**: 专门初始化问卷相关的数据库表

**使用方法**:
```bash
python scripts/init_questionnaire_db.py
```

**功能**:
- 创建问卷相关表
- 添加默认问卷题目
- 配置评分规则

**注意事项**:
- ⚠️ 会覆盖现有问卷数据

---

### 数据库迁移

#### 3. `migrate_db.py` - 数据库迁移
**用途**: 执行数据库迁移，更新表结构

**使用方法**:
```bash
python scripts/migrate_db.py
```

**功能**:
- 自动检测模型变化
- 生成迁移脚本
- 应用迁移到数据库

**注意事项**:
- ✅ 保留现有数据
- ⚠️ 迁移前建议备份数据库

---

#### 4. `update_db_schema.py` - 更新数据库模式
**用途**: 手动更新数据库表结构

**使用方法**:
```bash
python scripts/update_db_schema.py
```

**功能**:
- 添加新字段
- 修改字段类型
- 添加索引

**注意事项**:
- ⚠️ 需要手动编写更新逻辑
- ⚠️ 谨慎操作，可能影响现有数据

---

#### 5. `update_submission_model.py` - 更新提交模型
**用途**: 专门更新提交记录相关的表结构

**使用方法**:
```bash
python scripts/update_submission_model.py
```

**功能**:
- 更新 Submission 模型
- 添加新字段
- 修改关系

---

### 数据维护

#### 6. `clean_db.py` - 清空数据库
**用途**: 清空所有表数据（用于开发环境）

**使用方法**:
```bash
python scripts/clean_db.py
```

**功能**:
- 删除所有表中的数据
- 保留表结构

**注意事项**:
- ⚠️ **危险操作**！会删除所有数据
- ⚠️ 仅在开发环境使用
- ⚠️ 生产环境禁用

---

#### 7. `add_questions_direct.py` - 直接添加问题
**用途**: 直接向数据库添加问卷问题

**使用方法**:
```bash
python scripts/add_questions_direct.py
```

**功能**:
- 批量添加问卷问题
- 设置问题类型和选项
- 配置分值

**注意事项**:
- ⚠️ 会覆盖重复的问题

---

#### 8. `add_questions_manual.py` - 手动添加问题
**用途**: 通过交互式界面手动添加问题

**使用方法**:
```bash
python scripts/add_questions_manual.py
```

**功能**:
- 逐个添加问题
- 实时预览
- 支持修改和删除

**注意事项**:
- ✅ 适合少量问题添加
- ⚠️ 大量问题建议使用脚本

---

## 📋 常用场景

### 场景 1: 首次安装

```bash
# 1. 初始化数据库
python scripts/init_db.py

# 2. 初始化问卷数据库
python scripts/init_questionnaire_db.py

# 3. 启动应用
python run.py
```

---

### 场景 2: 数据库迁移

```bash
# 1. 备份数据库（手动复制 instance/anti_fraud_dev.db）

# 2. 执行迁移
python scripts/migrate_db.py

# 3. 验证迁移结果
python run.py
```

---

### 场景 3: 开发环境重置

```bash
# ⚠️ 警告：清空所有数据！

# 1. 清空数据库
python scripts/clean_db.py

# 2. 重新初始化
python scripts/init_db.py
python scripts/init_questionnaire_db.py
```

---

### 场景 4: 添加新问题

**方法 1: 批量添加**
```bash
python scripts/add_questions_direct.py
```

**方法 2: 手动添加**
```bash
python scripts/add_questions_manual.py
```

---

## ⚠️ 重要提示

### 安全警告

1. **备份数据库**
   - 执行任何脚本前，先备份 `instance/anti_fraud_dev.db`
   - 生产环境禁用这些脚本

2. **开发环境专用**
   - 这些脚本仅供开发使用
   - 生产环境需要额外的权限控制

3. **数据不可恢复**
   - `clean_db.py` 等脚本会永久删除数据
   - 执行前务必确认

---

### 最佳实践

1. **版本控制**
   - 脚本文件应该提交到 Git
   - 执行结果（数据库）不应提交

2. **测试环境**
   - 先在测试环境验证脚本
   - 确认无误后再在生产环境使用

3. **文档记录**
   - 记录每次执行的脚本和时间
   - 记录遇到的问题和解决方案

---

## 🔍 故障排除

### 问题 1: 脚本执行失败

**可能原因**:
- 数据库连接失败
- 依赖包未安装
- 权限不足

**解决方法**:
```bash
# 1. 检查依赖
pip install -r requirements.txt

# 2. 检查数据库连接
# 查看 config/settings.py 中的配置

# 3. 查看详细错误信息
python scripts/xxx.py  # 查看完整报错
```

---

### 问题 2: 数据丢失

**恢复方法**:
```bash
# 1. 从备份恢复数据库
cp instance/anti_fraud_dev.db.backup instance/anti_fraud_dev.db

# 2. 重新初始化
python scripts/init_db.py
```

---

### 问题 3: 迁移冲突

**解决方法**:
```bash
# 1. 删除迁移历史
rm -rf migrations/*

# 2. 重新初始化迁移
flask db init
flask db migrate -m "initial"
flask db upgrade
```

---

## 📖 相关文档

- [项目结构说明](PROJECT_STRUCTURE.md)
- [快速上手指南](../docs/guides/快速上手指南.md)
- [用户管理功能说明](../docs/features/用户管理功能说明.md)

---

**更新时间**: 2026-03-18  
**版本**: v3.0
