# create-fastapi 需求

**文档版本**：v1.0  
**创建日期**：20260626  
**最后更新**：20260626（v1.1 修订：生产部署以 uvicorn 为主）  

---

## 1. 项目概述

### 1.1 背景与目标

- **业务背景**：FastAPI 已成为 Python 异步 Web API 的主流选择，但社区缺少与 [create-flask](https://github.com/xiongxianzhu/create-flask) 同等定位的、基于现代工具链（uv、Pydantic 2、SQLModel、Typer）的一键脚手架。开发者每次新建项目需重复搭建目录结构、依赖配置、数据库会话、异常处理与部署模板，成本高且风格不一。
- **核心目标**：提供一条命令即可生成**生产可用**的现代 FastAPI 项目骨架；生成后由用户自行 `uv sync`、迁移与启动，工具**不得**代跑任何初始化命令。
- **目标用户**：
  - 需要快速启动 API 服务的 Python 后端开发者
  - 希望统一团队工程规范的技术负责人
  - 需要可定制模板、可 CI 集成的平台/工具维护者

### 1.2 范围边界

- **范围内**：
  - Typer CLI 工具 `create-fastapi` 的实现与发布
  - 内置 Jinja2 模板及模板渲染、可选模块门控
  - 支持本地目录 / git 仓库作为外部模板来源
  - 生成纯 API 项目（前后端分离，不含静态页与 Jinja 模板渲染）
  - 可选 Redis、Celery、Docker 模块
  - 生产部署模板（uvicorn + supervisor + nginx）
  - 单元测试骨架与健康检查示例
- **范围外**：
  - 不实现业务功能（用户系统、支付、消息队列业务逻辑等）
  - 生成后**不得**自动执行 `uv sync`、`alembic upgrade`、容器构建或服务启动
  - 不内置完整认证方案（JWT/OAuth2 仅提供扩展点与占位依赖，不作为 P0）
  - 不提供 GUI、Web 控制台或在线生成器
  - 不维护 FastAPI 框架本身或第三方库

---

## 2. 功能需求

### 2.1 功能列表

| 序号 | 功能模块 | 描述 | 优先级 |
|------|----------|------|--------|
| 1 | CLI 入口 | `create-fastapi <name>` 命令行生成项目 | P0 |
| 2 | 项目名校验 | 校验命名规则与目标路径冲突 | P0 |
| 3 | 内置模板渲染 | Jinja2 渲染占位变量与模块门控 | P0 |
| 4 | 生成项目骨架 | 输出完整 FastAPI 工程目录与配置文件 | P0 |
| 5 | 可选模块 | `--redis` / `--celery` / `--docker` 条件生成 | P0 |
| 6 | 自定义模板 | 本地路径 / git 浅克隆模板 | P1 |
| 7 | 覆盖与交互 | `--force` 覆盖、`--yes` 跳过确认 | P1 |
| 8 | 版本与帮助 | `--version`、`--help` | P0 |
| 9 | 工具自身测试 | pytest 覆盖 CLI 与渲染逻辑 | P0 |
| 10 | 文档与发布 | README、PyPI / git 安装说明 | P1 |

### 2.2 详细需求

#### 2.2.1 CLI 入口与安装

- **需求描述**：应提供全局可安装的 CLI 包 `create-fastapi`，命令形如 `create-fastapi my-api [OPTIONS]`。
- **验收标准**：
  - 给定 Python 3.13+ 环境，执行 `uv tool install git+https://github.com/xiongxianzhu/create-fastapi.git` 后，`create-fastapi --version` 应输出版本号。
  - 执行 `create-fastapi --help` 应列出全部参数说明。
  - 在工具仓库内执行 `uv run create-fastapi my-api` 应无需全局安装即可生成项目。
- **安装方式**（文档中应说明，实现应兼容）：
  - `uv tool install create-fastapi`（PyPI 发布后）
  - `pip install` / `pipx install`
  - 本地开发：`git clone` + `uv sync` + `uv run create-fastapi`

#### 2.2.2 项目名校验与目标路径

- **需求描述**：`<name>` 作为项目标识，用于目录名与包名推导。
- **验收标准**：
  - 项目名应为小写，允许 `-` 分隔；**不得**含 `_`、空格或特殊字符；不符合时应报错并退出码非 0。
  - 默认在当前目录创建 `<name>/`；`--path ./services` 时应在 `./services/<name>/` 创建。
  - 目标目录已存在且未指定 `--force` 时，应跳过或提示确认（默认可跳过已存在文件，与 create-flask 行为一致）。
  - `package_name` 应由 `project_name` 将 `-` 替换为 `_` 得到，用于 Python 包导入路径。

#### 2.2.3 CLI 参数

| 参数 | 说明 | 优先级 |
|------|------|--------|
| `<name>` | 项目名 | P0 |
| `--path` | 父目录，默认当前目录 | P0 |
| `--redis` / `--no-redis` | 集成 Redis 客户端（可选，默认关闭） | P0 |
| `--celery` | 集成 Celery；**必须**自动启用 Redis | P0 |
| `--docker` | 生成 Dockerfile、docker-compose、.dockerignore | P0 |
| `--template`, `-t` | 模板来源：内置（默认）/ 本地路径 / git URL | P1 |
| `--template-ref` | git 模板分支或标签 | P1 |
| `--template-subdir` | git 仓库内模板根子目录 | P1 |
| `--force` | 覆盖已存在文件 | P1 |
| `--yes`, `-y` | 跳过交互确认 | P1 |

- **验收标准**：
  - 同时指定 `--celery` 与 `--no-redis` 时，应报错并说明 Celery 依赖 Redis。
  - 指定 `--celery` 时，生成产物应包含 Celery 配置与示例任务，且 `use_redis=true`。
  - 未指定 `--docker` 时，**不得**生成 Docker 相关文件。

#### 2.2.4 工具本身技术栈（create-fastapi CLI）

| 类别 | 技术 | 说明 |
|------|------|------|
| 语言 | Python 3.13+ | 与生成项目一致 |
| CLI | Typer | 子命令与选项解析 |
| 模板 | Jinja2 | 文本渲染与文件名渲染 |
| 打包 | hatchling | `pyproject.toml` 构建 |
| 开发 | uv · pytest · ruff · mypy | 工具仓库自检 |

- **验收标准**：
  - 运行时依赖**仅** Typer + Jinja2（git 模板克隆调用系统 `git`，不纳入 Python 依赖）。
  - 工具仓库应可通过 `uv run pytest`、`uv run ruff check .`、`uv run mypy` 通过 CI。

#### 2.2.5 生成项目技术栈（`create-fastapi my-api` 产物）

| 类别 | 技术 | 说明 |
|------|------|------|
| 运行时 | Python 3.13 · uv | 依赖管理与锁文件 |
| Web | FastAPI | 纯 APIRouter + 依赖注入 |
| 校验 / 配置 | Pydantic 2 · pydantic-settings | 请求/响应模型与环境配置 |
| 数据 | SQLModel · Alembic | async session；`table=True` 表模型；内置 SQLAlchemy 2.0 |
| DB 驱动 | asyncpg（PostgreSQL） | 默认异步 PostgreSQL；`.env.example` 提供 SQLite 测试说明 |
| 代码质量 | ruff · mypy | lint / format / 类型检查 |
| ASGI 服务 | uvicorn | 开发与生产统一使用；开发 `--reload`，生产 `--workers` + supervisor |
| 反向代理 | nginx · supervisor | nginx 前置；supervisor 托管 uvicorn 进程 |

- **设计原则**：
  - **不得**依赖 Flask-RESTful、Flask-Smorest、Marshmallow 等 Flask 生态包。
  - **默认**使用 [SQLModel](https://github.com/fastapi/sqlmodel) 作为 ORM（内置 SQLAlchemy 2.0 + Pydantic）；`models/` 放 `table=True`，`schemas/` 放 API 入出参。
  - 参考 [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) 的路由拆分、`SessionDep`、Settings 与 Docker 流水线思路，但不引入 React / Traefik 全栈部分。
  - 采用 **async SQLModel session**，路由处理函数默认为 `async def`。

#### 2.2.6 生成项目目录结构

```text
my-api/
├── app/
│   ├── main.py              # create_app()：FastAPI 实例 + lifespan + 路由挂载
│   ├── core/
│   │   ├── config.py        # Settings（pydantic-settings）
│   │   ├── exceptions.py    # 统一异常类 + exception_handler 注册
│   │   ├── constants.py     # 常量 / 枚举
│   │   └── security.py      # 鉴权依赖占位（Depends 扩展点）
│   ├── db/
│   │   └── session.py       # async engine、AsyncSession、get_db / SessionDep
│   ├── api/
│   │   ├── deps.py          # 公共 Depends（如 get_db、分页）
│   │   └── v1/
│   │       ├── router.py    # 聚合 v1 路由
│   │       ├── endpoints/
│   │       │   └── health.py
│   │       └── admin/       # 可选：管理端路由前缀 /api/admin/v1
│   │           └── endpoints/
│   │               └── health.py
│   ├── models/              # SQLModel 表模型（table=True）
│   ├── schemas/             # SQLModel API 入出参（无 table）
│   ├── services/            # 业务逻辑（与框架解耦）
│   ├── tasks/               # 仅 --celery：Celery 任务
│   ├── celery_app.py        # 仅 --celery
│   └── celeryconfig.py      # 仅 --celery
├── alembic/                 # Alembic 迁移目录 + env.py
├── deploy/
│   ├── supervisor/          # {{ project_name }}.conf：command 为 uvicorn app.main:app ...
│   └── nginx/               # 反向代理示例（可选）
├── tests/
│   ├── conftest.py          # TestClient + 测试 DB / override deps
│   └── test_health.py
├── logs/.gitkeep
├── alembic.ini
├── pyproject.toml           # 可含 [project.scripts] 或文档化 uvicorn 启动命令
├── .env.example
├── .python-version          # 3.13
├── .gitignore
└── README.md                # 生成后用户自行 uv sync / migrate / run 的说明
```

- **验收标准**：
  - 生成后目录结构与上述一致（可选模块除外）；空目录以 `.gitkeep` 占位。
  - `app/main.py` 应通过 `lifespan` 管理 DB 引擎/连接池的 startup 与 shutdown。
  - 应注册全局异常处理器，错误响应 JSON 结构统一（含 `code`、`message` 字段）。
  - C 端健康检查：`GET /api/v1/health` 返回 200；若生成 admin 路由，则 `GET /api/admin/v1/health` 可带鉴权占位。
  - OpenAPI 文档应可通过 `/docs` 与 `/redoc` 访问（FastAPI 默认行为，模板不得禁用）。
  - `deploy/supervisor/` 模板应直接以 uvicorn 作为进程 command，**不得**默认使用 gunicorn。

#### 2.2.7 分层与编码约定

- **路由层**（`api/v1/endpoints/`）：仅负责 HTTP 语义、调用 service、声明 `response_model`；**不得**编写复杂业务逻辑。
- **服务层**（`services/`）：业务逻辑，接收 session / 领域对象，便于单测。
- **模型层**（`models/`）：SQLModel `table=True`；提供 `TimestampMixin`。
- **Schema 层**（`schemas/`）：SQLModel 无表模型；区分 `Create` / `Read` 模式（示例见 `schemas/common.py`）。
- **依赖注入**：`SessionDep = Annotated[AsyncSession, Depends(get_db)]`。
- **配置**：`Settings` 从环境变量 / `.env` 读取；`.env.example` 须含 `DATABASE_URL`、`APP_ENV`、Redis/Celery 占位项。
- **验收标准**：
  - 示例 `health` 接口应使用 `APIRouter`，并在 `router.py` 中 `include_router`。
  - `tests/conftest.py` 应提供 `TestClient` fixture，测试数据库可使用 SQLite 内存或独立 test URL（文档说明）。

#### 2.2.8 可选模块

##### Redis（`--redis`）

- 应生成 Redis 连接配置与 lifespan 或依赖封装（推荐 `redis.asyncio`）。
- `.env.example` 应增加 `REDIS_URL`。
- **不得**在未指定 `--redis` 时引入 redis 依赖。

##### Celery（`--celery`）

- 应生成 `celery_app.py`、`celeryconfig.py`、`app/tasks/` 示例任务。
- **必须**同时启用 Redis（broker / result backend）。
- supervisor 模板应包含 celery worker 进程配置（可与 create-flask 对齐命名：`{{ project_name }}-celery.conf`）。

##### Docker（`--docker`）

- 应生成：
  - `Dockerfile`（多阶段或 slim 镜像，基于 uv 安装依赖）
  - `docker-compose.yml`（app + postgres [+ redis 若启用]）
  - `.dockerignore`
- 镜像默认 CMD 应使用 uvicorn 启动 ASGI 应用，例如 `uvicorn app.main:app --host 0.0.0.0 --port 8000`；多 worker 场景使用 `--workers N`。

#### 2.2.9 自定义模板

- **需求描述**：`-t` 支持三种来源，渲染规则与内置模板一致。
- **验收标准**：
  - 内置（默认）：不传 `-t` 时使用包内模板。
  - 本地目录：`-t ./my-template` 从路径读取。
  - git 仓库：浅克隆指定 ref，渲染后**必须**清理临时克隆目录；克隆产物中的 `.git/` **不得**进入生成项目。
  - URL 识别：`http(s)://`、`git@`、`ssh://`、`git://` 或以 `.git` 结尾视为 git；否则视为本地路径。
  - git 来源时系统无 `git` 命令应报错提示安装。

**外部模板约定**（与 create-flask 对齐）：

| 占位变量 | 含义 |
|----------|------|
| `{{ project_name }}` | CLI 传入的项目名 |
| `{{ package_name }}` | `-` → `_` 的包名 |
| `use_redis` | 是否启用 Redis 模块 |
| `use_celery` | 是否启用 Celery 模块 |
| `use_docker` | 是否启用 Docker 模块 |

- **点文件占位名**：`gitignore`、`dockerignore`、`python-version`、`env.example` → 生成时自动加点前缀。
- **模块门控**：Celery 相关文件仅 `use_celery`；Docker 三件套仅 `use_docker`。
- **路径示例**：`deploy/supervisor/{{ project_name }}.conf` → `deploy/supervisor/my-api.conf`。
- 非文本文件原样复制；空目录用 `.gitkeep`。

#### 2.2.10 生成后用户流程（写入 README，工具不执行）

文档应明确列出用户**自行**执行的步骤，例如：

```bash
cd my-api
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

生产环境应说明 `uv sync --frozen --no-dev`，以及 supervisor 直接拉起 uvicorn（如 `uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4`）与 nginx 反向代理配置路径。**不得**将 gunicorn 作为默认生产方案；若用户需要进程管理器 + worker 类组合，可在 README 附录中简要说明 gunicorn + `uvicorn.workers.UvicornWorker` 为可选替代，但不生成 `gunicorn.conf.py` 模板。

---

## 3. 非功能需求

### 3.1 性能

- CLI 在内置模板上生成完整项目，耗时应 **< 3 秒**（不含 git 模板克隆）。
- git 模板浅克隆超时应有合理上限（建议 60 秒）并给出可读错误信息。

### 3.2 安全

- 工具**不得**在生成文件中写入真实密钥；`.env.example` 仅含占位符。
- git 克隆应使用浅克隆（`--depth 1`）以减少攻击面与耗时。
- 模板渲染**不得**执行任意 Python 代码（仅 Jinja2 变量替换与条件块）。

### 3.3 兼容性与可维护性

- 支持 macOS、Linux；Windows 上路径与换行应可正常工作（CI 至少覆盖 Linux）。
- 生成项目 `pyproject.toml` 应 pin 主要依赖下限版本，并提交 `uv.lock`。
- 工具与模板代码应通过 ruff format/check，mypy 严格模式可渐进启用。

### 3.4 可测试性

- 工具仓库测试覆盖率：CLI 参数组合、模板门控、项目名校验、git/本地模板解析至少各 1 组用例。
- 生成项目应包含可运行的 `test_health.py`，在 `uv sync` 后 `uv run pytest` 应通过。

---

## 4. 数据与接口

### 4.1 工具 CLI 接口

```text
create-fastapi <name> [OPTIONS]
```

- **输入**：项目名、选项 flags、可选模板来源。
- **输出**：文件系统上的项目目录；stdout 打印生成路径与后续步骤提示；失败时 stderr 错误信息与非零退出码。

### 4.2 生成项目的 API 约定（示例）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health` | 健康检查，返回服务状态 |
| GET | `/api/admin/v1/health` | 管理端健康检查（若生成 admin 路由） |
| GET | `/docs` | Swagger UI（FastAPI 默认） |
| GET | `/redoc` | ReDoc（FastAPI 默认） |

### 4.3 数据模型（生成项目示例）

- 模板可含示例 ORM 模型（如 `Item` 或仅 `Base` + mixin），用于演示 Alembic 迁移流程；**不得**绑定具体业务表结构作为 P0 交付物。

### 4.4 统一错误响应格式

```json
{
  "code": "VALIDATION_ERROR",
  "message": "请求参数校验失败",
  "details": []
}
```

- HTTP 状态码与 FastAPI `HTTPException` / 自定义 `APIException` 一致；422 校验错误应被 exception_handler 格式化为此结构。

---

## 5. 约束与假设

### 5.1 技术约束

- Python **3.13+** 为工具与生成项目的最低版本。
- 包管理**必须**以 uv 为一等公民（`pyproject.toml` + `uv.lock`）。
- 参考实现：[create-flask](https://github.com/xiongxianzhu/create-flask) 的 CLI 行为、模板约定与模块门控，API 层按 FastAPI  idioms 重写。
- 许可证：MIT（与 create-fastapi 仓库一致）。

### 5.2 业务假设

- 目标用户熟悉 uv 与基本 FastAPI 概念。
- 生产数据库默认 PostgreSQL；本地开发可用 Docker Compose 或本地 PG 实例。
- 用户自行负责密钥管理、HTTPS 与云基础设施。

### 5.3 依赖项

- 系统：`git`（仅在使用 git 模板时）。
- 网络：git 模板克隆、PyPI / uv 安装依赖时需联网。

---

## 6. 里程碑建议（实现顺序）

| 阶段 | 交付物 | 说明 |
|------|--------|------|
| M1 | CLI 骨架 + 内置模板 + 核心目录 | P0 可生成可运行最小 FastAPI 项目 |
| M2 | Alembic + 测试 + 异常与 health | 可迁移、可 pytest |
| M3 | Redis / Celery / Docker 门控 | 与 create-flask 特性对齐 |
| M4 | 外部模板 + `--force` / `-y` | P1 完成 |
| M5 | README、CI、PyPI 发布 | 对外可用 |

---

## 7. 附录

### 7.1 术语表

| 术语 | 含义 |
|------|------|
| create-fastapi | 本项目 CLI 工具包名与命令名 |
| 生成项目 | 用户运行 CLI 后在磁盘上得到的 FastAPI 工程 |
| 模块门控 | 根据 CLI flags 条件渲染或跳过模板文件 |
| lifespan | FastAPI 应用生命周期钩子，用于 startup/shutdown |
| package_name | 由项目名推导的 Python 包名（`-` → `_`） |

### 7.2 与 create-flask 的差异摘要

| 维度 | create-flask | create-fastapi |
|------|--------------|----------------|
| Web 框架 | Flask 蓝图 + 视图函数 | FastAPI APIRouter + Depends |
| ORM 集成 | Flask-SQLAlchemy | SQLModel async |
| 迁移 | Flask-Migrate | Alembic |
| 入口 | wsgi.py + gunicorn | app.main:app + uvicorn（开发 `--reload`，生产 `--workers`） |
| 校验 | Pydantic（手动） | Pydantic（FastAPI 原生） |
| 异步 | 同步为主 | async 路由 + async session 为主 |

### 7.3 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 20260626 | v1.0 | 初稿 | — |
| 20260626 | v1.2 | 数据层改为 SQLModel（替代直接使用 SQLAlchemy 2.0） | — |
