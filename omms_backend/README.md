# OMMS Backend (Online Medical Management System)

## 简介

在线医疗管理系统 (OMMS) 的后端服务，基于 Python 3 和 FastAPI 框架开发。提供 RESTful API 接口，支持预约挂号、病历管理、药品库存、在线支付等核心功能。

## 技术栈

- **语言**: Python 3.10+
- **Web 框架**: FastAPI
- **ASGI 服务器**: Uvicorn
- **ORM**: SQLAlchemy (Async)
- **数据验证**: Pydantic v2
- **数据库迁移**: Alembic
- **数据库**: MySQL 5.5.62
- **认证**: JWT (JSON Web Tokens)

## 目录结构 (规划)

```
omms_backend/
├── app/
│   ├── api/            # API 路由定义
│   ├── core/           # 核心配置 (统一响应等)
│   ├── db/             # 数据库连接与会话
│   ├── models/         # SQLAlchemy 数据模型
│   │   ├── __init__.py # Base 声明
│   ├── schemas/        # Pydantic 数据验证模型 (DTOs)
│   ├── server.py       # 应用入口
│   └── settings.py     # 环境变量与数据库配置
├── scripts/            # 开发/运维辅助脚本
│   └── init_db.py      # 数据库重建与开发数据初始化
├── .env.example        # 环境变量示例
├── requirements.txt    # 项目依赖
└── README.md           # 项目文档
```

数据库结构定义文件：

- 仓库根目录：[`docs/omms.sql`](../docs/omms.sql)

## 快速开始

### 1. 环境准备

确保本地已安装：

- Python 3.10 或更高版本
- MySQL 5.5.62
- Git

### 2. 克隆项目

```bash
git clone <repository_url>
cd omms/omms_backend
```

### 3. 创建虚拟环境并激活

建议使用 `venv` 或 `conda` 管理虚拟环境。

#### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
# 或者如果使用 poetry
# poetry install
```

_(注意：项目初期可能暂无 `requirements.txt`，请先安装核心依赖)_

```bash
pip install fastapi uvicorn[standard] sqlalchemy pymysql aiomysql pydantic pydantic-settings alembic python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv
```

### 5. 配置环境变量

复制 `.env.example` 为 `.env` 并修改数据库配置：

```ini
# .env
PROJECT_NAME="OMMS"
API_V1_STR=""

# Database
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_SERVER=localhost
MYSQL_PORT=3306
MYSQL_DB=medical_system

# Security
SECRET_KEY=your-secret-key-please-change-it
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 6. 数据库初始化

确保 MySQL 中已创建数据库：

```sql
CREATE DATABASE medical_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

运行数据库迁移（应用表结构）：

```bash
# 初始化 alembic (如果是第一次)
# alembic init alembic

# 生成迁移脚本
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

### 7. 开发数据一键初始化

使用脚本快速迁移结构并清洗/导入预设数据，支持本地与服务器：

```powershell
# 查看帮助
python omms_backend/scripts/init_db.py --help

# 常用：迁移结构 + 清洗并灌入演示数据（默认模式，适合经常运行）
python omms_backend/scripts/init_db.py --mode app

# 仅迁移结构（不执行 docs/omms.sql，不删库）
python omms_backend/scripts/init_db.py --mode migrate

# 完整建库（执行 docs/omms.sql 的 DROP/CREATE），再灌入演示数据
python omms_backend/scripts/init_db.py --mode full

# 指定 SQL 文件路径（配合 --mode full）
python omms_backend/scripts/init_db.py --mode full --sql D:/data/omms.sql

# 使用 SQLite（本地测试）
python omms_backend/scripts/init_db.py --sqlite --mode app --seed-count 20

# 自定义数据库连接（覆盖 `.env` 的 MySQL 连接）
python omms_backend/scripts/init_db.py --dsn "mysql+aiomysql://user:pass@host:3306/medical_system" --mode app
```

脚本行为说明：

- 结构迁移（无删库）：
  - 自动对齐与后端模型一致的列、索引与外键，包括：
    - `departments`: 增加 `parent_id`、`sort_order`
    - `doctors`: 将 `name` 调整为 `doctor_name`、增加 `dept_id` 外键、将 `intro` 调整为 `introduction`、移除旧 `department` 文本列
    - `doctor_schedules`: 增加 `booked`
    - `appointments`: 增加 `schedule_id` 及外键
  - 若结构已正确，迁移步骤将跳过（幂等）。
- 数据清洗与写入（示例数据）：
  - 清空并写入：`departments`、`doctors`、`doctor_schedules`、`appointments`、`patients`、`medical_records`、`record_templates`
  - 用户数据通过 `upsert` 写入，避免重复。

建议：

- 经常运行建议使用 `--mode app`，该模式会先进行“结构迁移”，然后清洗并灌入演示数据，不删除数据库或表。
- 仅需修复库结构时使用 `--mode migrate`；需要彻底重建时使用 `--mode full`。

### 8. 启动服务

开发模式（支持热重载）：

```bash
uvicorn app.server:app --reload --host 0.0.0.0 --port 8000
```

### 9. 访问接口文档

启动成功后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 架构说明

- 新增业务路由置于 `app/api/`，通过 `app/api/__init__.py` 聚合后由 `app/server.py` 在 `"/api"` 前缀下统一挂载。
- 路由前缀：`/api` 当前固定；`API_V1_STR` 尚未启用，后续如需版本化可与该变量结合使用。

## 开发规范

- **代码格式化**: 使用 `black` 和 `isort`。
- **风格检查**: 使用 `flake8` 或 `ruff`。

## 认证与鉴权

- 认证方式：JWT，登录成功后返回 `accessToken`。
- 认证接口：
  - `POST /api/auth/register` 注册用户（默认赋予 PATIENT 身份）
  - `POST /api/auth/login` 用户登录（支持用户名或邮箱），返回 JWT
  - `GET /api/auth/me` 获取当前登录用户信息
- 请求头：`Authorization: Bearer <accessToken>`。
- 鉴权范围：`/api` 前缀下除 `auth` 路由外的所有接口均需携带有效 JWT。
- 角色与权限：
  - 四种身份组：`ADMIN`、`DOCTOR`、`NURSE`、`PATIENT`
  - 可在路由中使用依赖实现细粒度控制：
    - 按角色：`Depends(require_role_in(["ADMIN", "DOCTOR"]))`
    - 按权限码：`Depends(require_perm_codes(["record:manage"]))`
