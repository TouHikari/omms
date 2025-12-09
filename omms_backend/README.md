# OMMS Backend (Online Medical Management System)

## 简介

在线医疗管理系统 (OMMS) 的后端服务，基于 Python 3 和 FastAPI 框架开发。提供 RESTful API 接口，支持预约挂号、病历管理、药房管理（进销存）、报表统计等核心功能。

## 技术栈

- **语言**: Python 3.10+
- **Web 框架**: FastAPI
- **ASGI 服务器**: Uvicorn
- **ORM**: SQLAlchemy (Async)
- **数据验证**: Pydantic v2
- **数据库迁移**: Alembic
- **数据库**: MySQL 5.5.62
- **认证**: JWT (JSON Web Tokens)

## 目录结构

```
omms_backend/
├── app/
│   ├── api/            # API 路由定义
│   │   ├── appointments/ # 预约、科室、医生、排班模块
│   │   ├── auth.py       # 认证模块
│   │   ├── pharmacy.py   # 药房模块
│   │   ├── records.py    # 病历模块
│   │   ├── reports.py    # 报表统计模块
│   │   └── __init__.py   # 路由聚合
│   ├── core/           # 核心配置 (统一响应、认证依赖、安全配置等)
│   ├── db/             # 数据库连接与会话管理
│   ├── models/         # SQLAlchemy 数据模型
│   │   ├── __init__.py     # Base 声明
│   │   ├── appointment.py  # 预约相关模型
│   │   ├── inventory.py    # 库存相关模型
│   │   ├── medicine.py     # 药品信息模型
│   │   ├── patient.py      # 患者信息模型
│   │   ├── prescription.py # 处方相关模型
│   │   ├── record.py       # 病历相关模型
│   │   ├── supplier.py     # 供应商相关模型
│   │   └── user.py         # 系统用户模型
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

# 生成迁移脚本 (仅在修改模型后需要)
# alembic revision --autogenerate -m "Add pharmacy tables"

# 应用迁移
alembic upgrade head
```

### 7. 开发数据一键初始化

使用脚本快速迁移结构并清洗/导入预设数据（包含科室、医生、患者、药品、库存、处方等演示数据）：

```powershell
# 查看帮助
python scripts/init_db.py --help

# 常用：迁移结构 + 清洗并灌入演示数据（默认模式，适合经常运行）
python scripts/init_db.py --mode app

# 仅迁移结构（不执行 docs/omms.sql，不删库）
python scripts/init_db.py --mode migrate

# 完整建库（执行 docs/omms.sql 的 DROP/CREATE），再灌入演示数据
python scripts/init_db.py --mode full

# 指定 SQL 文件路径（配合 --mode full）
python scripts/init_db.py --mode full --sql D:/data/omms.sql
```

脚本会自动处理：
- 数据库表结构同步
- 初始化基础数据（科室、医生、药品目录）
- 生成模拟业务数据（患者、预约、病历、处方、库存变动）

### 8. 启动服务

开发模式（支持热重载）：

```bash
uvicorn app.server:app --reload --host 0.0.0.0 --port 8000
```

### 9. 访问接口文档

启动成功后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 功能模块

### 核心业务
- **预约挂号**: 科室管理、医生排班、患者预约、号源管理。
- **病历管理**: 电子病历（EMR）、病历模板、诊断记录。
- **药房管理**:
    - **药品库**: 药品基础信息、规格、生产厂家。
    - **库存**: 批次管理、入库、出库、有效期预警、低库存预警。
    - **供应商**: 供应商信息与采购订单。
    - **处方**: 处方开立、审核与发药。
- **报表统计**:
    - **就诊日报/月报**: 门诊量、预约量统计。
    - **药品统计**: 药品销售排行、发药量统计。

### 系统管理
- **认证授权**: 基于 JWT 的用户认证，支持多角色（管理员、医生、护士、患者）。
- **权限控制**: 基于角色的访问控制 (RBAC)。

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
