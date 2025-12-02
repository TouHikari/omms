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
│   ├── core/           # 核心配置 (config, security, exceptions)
│   ├── db/             # 数据库连接与会话
│   ├── models/         # SQLAlchemy 数据模型
│   ├── schemas/        # Pydantic 数据验证模型 (DTOs)
│   ├── services/       # 业务逻辑层
│   ├── utils/          # 工具函数
│   └── main.py         # 应用入口
├── alembic/            # 数据库迁移脚本
├── tests/              # 测试用例
├── .env.example        # 环境变量示例
├── alembic.ini         # Alembic 配置
├── pyproject.toml      # 项目依赖管理 (或 requirements.txt)
└── README.md           # 项目文档
```

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
pip install fastapi uvicorn[standard] sqlalchemy pymysql aiomysql pydantic pydantic-settings alembic python-jose[cryptography] passlib[bcrypt] python-multipart
```

### 5. 配置环境变量

复制 `.env.example` 为 `.env` 并修改数据库配置：

```ini
# .env
PROJECT_NAME="OMMS Backend"
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

### 7. 启动服务

开发模式（支持热重载）：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. 访问接口文档

启动成功后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 开发规范

- **代码格式化**: 使用 `black` 和 `isort`。
- **风格检查**: 使用 `flake8` 或 `ruff`。
- **Git 提交信息**: 遵循 Conventional Commits 规范 (e.g., `feat: add login api`, `fix: resolve db connection issue`)。

## 许可证

MIT
