# Voxel FastAPI Admin

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116%2B-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2%20Async-D71F00?logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported-4169E1?logo=postgresql&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Supported-4479A1?logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Supported-DC382D?logo=redis&logoColor=white)
![License](https://img.shields.io/badge/License-Apache_2.0-blue)
![Version](https://img.shields.io/badge/version-1.1.0--SNAPSHOT-orange)

**Voxel FastAPI Admin** 是面向中后台管理端的 FastAPI 异步后端：扁平 DDD（**无 `src/`**），仅提供 **Admin** API（`/api/v1/admin/**`）。

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [工程结构](#工程结构)
- [快速开始](#快速开始)
- [默认账号](#默认账号)
- [License](#license)

## 功能特性

API 前缀为 `/api/v1/admin/*`：

| 模块 | 说明 |
| --- | --- |
| 账号体系 | ADMIN 会话（HttpOnly Cookie / Authorization）；密码 RSA 传输、验证码、失败锁定与限流；可配置三方 OAuth |
| RBAC 权限 | 账号 / 角色 / 部门 / 用户组 / 岗位；菜单、按钮与 API 资源授权；在线会话踢出 |
| 系统管理 | 字典、动态配置（敏感项 Fernet 加密）、Banner、公告 / 通知、意见反馈、弱口令库 |
| 对象存储 | S3 兼容存储，直链或预签名访问 |
| 运维能力 | 操作审计、登录日志、工作台概览、内置任务调度（`sys_job`；种子任务默认禁用，需在管理端启用） |
| 代码生成 | 单表 / 树表 / 主子表，预览与 ZIP 下载 |
| 实名认证 | 工单提交与审核、敏感字段加密存储 |
| 业务扩展 | 领域模块可按同样扁平 DDD 模式横向扩展 |

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 后端 | Python 3.11+ · FastAPI · uvicorn / gunicorn · Pydantic Settings |
| 持久化 | PostgreSQL / MySQL · SQLAlchemy 2（async）· Alembic · asyncpg / aiomysql |
| 缓存 / 会话 | Redis |
| 文档 | OpenAPI（`/docs`、`/redoc`，可按配置开关） |
| 其他 | boto3 · croniter · cryptography · OpenTelemetry（可选） |

## 工程结构

```text
voxel-fastapi-admin/
├── voxel_types/          # types 层（避免遮蔽标准库 types）
├── api/                  # 契约层
├── domain/               # 领域层
├── infrastructure/       # 基础设施
├── cases/                # 用例编排
├── trigger/              # HTTP 等入口
├── app/                  # 进程入口（main / lifespan）
├── scripts/              # MySQL 建表+种子
├── migrations/           # Alembic 增量
└── tests/
```

| 文件 / 目录 | 用途 |
| --- | --- |
| `scripts/voxel_fastapi.sql` | MySQL 建表+种子（无 DROP；`IF NOT EXISTS` / `INSERT IGNORE`） |
| `migrations/` | Alembic 增量表结构（见 [`migrations/README.md`](migrations/README.md)） |

## 快速开始

### 环境要求

- Python **3.11+**
- MySQL 8+（演示种子）、Redis
- PostgreSQL 亦可（Alembic 建表，见 `migrations/README.md`）

### 1. 初始化数据库

```bash
mysql -u root -p -e "CREATE DATABASE voxel_fastapi DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p voxel_fastapi < scripts/voxel_fastapi.sql
```

或空库增量：

```bash
pip install -e ".[dev,mysql]"   # 或 ".[dev,postgres]"
# 配置 DB__URL 后
alembic upgrade head
```

应用启动不执行迁移；`alembic upgrade head` 仅在维护时手动执行。配置密钥等见 `infrastructure/config/settings.py`（支持 `.env` / 环境变量，如 `DB__URL`、`REDIS__URL`、`APP__CONFIG_CRYPTO_KEY`）。

### 2. 启动后端

```bash
pip install -e ".[dev,mysql]"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8100 --reload
```

| 项 | 地址 |
| --- | --- |
| API | http://127.0.0.1:8100 |
| OpenAPI | http://127.0.0.1:8100/docs |
| ReDoc | http://127.0.0.1:8100/redoc |

工作区约定管理端端口为 `8100`（与 Boot `8000` / Gin `8200` 错开）。Linux / 容器可用 `./entrypoint.sh`（gunicorn）。

## 默认账号

| 端 | 地址 | 账号 | 密码 | 说明 |
| --- | --- | --- | --- | --- |
| Admin | http://127.0.0.1:8100 | `superadmin` | `123456` | 超级管理员（`*:*:*`） |

仅供本地演示。部署后请修改默认密码与敏感配置。更多种子见 `scripts/voxel_fastapi.sql`。

## License

本项目基于 Apache License 2.0 开源。
