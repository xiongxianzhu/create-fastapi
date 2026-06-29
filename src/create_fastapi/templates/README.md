<h1 align="center">{{ project_name }}</h1>

<p align="center">
  <sub>由 <a href="https://github.com/xiongxianzhu/create-fastapi">create-fastapi</a> 生成的 FastAPI 项目</sub>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.138+-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/></a>
  <a href="https://www.uvicorn.org/"><img src="https://img.shields.io/badge/uvicorn-0.49+-4051B5?style=flat-square" alt="uvicorn"/></a>
  <a href="https://github.com/fastapi/sqlmodel"><img src="https://img.shields.io/badge/SQLModel-0.0.39+-059669?style=flat-square&logo=fastapi&logoColor=white" alt="SQLModel"/></a>
  <a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-2-E92063?style=flat-square&logo=pydantic&logoColor=white" alt="Pydantic"/></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/uv-DE5FE9?style=flat-square&logo=uv&logoColor=white" alt="uv"/></a>
{% if use_redis %}  <img src="https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white" alt="Redis"/>
{% endif %}{% if use_celery %}  <img src="https://img.shields.io/badge/Celery-37814A?style=flat-square&logo=celery&logoColor=white" alt="Celery"/>
{% endif %}{% if use_docker %}  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
{% endif %}
</p>

---

## 快速开始

```bash
make install
make setup
make migrate
make dev
```

或手动：

```bash
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## FastAPI CLI

`pyproject.toml` 中已配置 `[tool.fastapi] entrypoint = "app.main:app"`，可直接使用 FastAPI 官方 CLI（随 `fastapi[standard]` 安装）：

```bash
# 开发（热重载，默认 http://127.0.0.1:8000）
uv run fastapi dev

# 指定 host / port
uv run fastapi dev --host 0.0.0.0 --port 8080

# 生产（无热重载；多 worker 示例）
uv run fastapi run --host 127.0.0.1 --port 8000 --workers 4
```

与 `make dev`（底层为 `uvicorn --reload`）等价；生产环境亦可继续用 supervisor 配置中的 `uvicorn` 命令。

健康检查 → `GET /api/v1/health` · 文档 → `/docs`

## 环境变量

`make setup` 或 `cp .env.example .env` 后，至少将 `SECRET_KEY` 改为随机强密钥（`.env.example` 中的占位值不可用于生产）：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

将输出填入 `.env` 的 `SECRET_KEY=` 即可；按需修改 `DATABASE_URL` 等其余项。

## 依赖说明

**要求**：Python 3.14+（见 `.python-version`）。

| 包 | 最低版本 |
|------|----------|
| `fastapi[standard]` | 0.138.1 |
| `uvicorn[standard]` | 0.49.0 |
| `pydantic-settings` | 2.14.2 |
| `sqlmodel` | 0.0.39 |
| `alembic` | 1.18.5 |
| `asyncpg` | 0.31.0 |
| `greenlet` | 3.5.3 |
| `python-dotenv` | 1.2.2 |

| 环境 | 命令 | 内容 |
|------|------|------|
| 开发 | `make install` / `uv sync` | 上表运行时依赖 + `dev` 组（ruff、mypy、pytest、httpx、aiosqlite） |
| 生产 | `make prod-install` | 运行时依赖（含 `[standard]` extras），`uv sync --frozen --no-dev` |

## 常用命令

| 场景 | 命令 |
|------|------|
| 帮助 | `make help` |
| 开发 | `make dev` · `uv run fastapi dev` |
| 生产运行 | `uv run fastapi run`（或 supervisor / uvicorn） |
| 迁移 | `make revision MSG="描述"` → `make migrate` |
| 质量 | `make lint` · `make typecheck` · `make test` · `make check` |
| 生产 | `make prod-install` → supervisor 拉起 uvicorn → nginx 反代 |
{% if use_celery %}| Worker | `make celery` |
{% endif %}{% if use_docker %}| 容器 | `make docker-up` · `make docker-down` |
{% endif %}

## 目录一览

```text
app/          main · core · db · api · models · schemas · services
alembic/      迁移
deploy/       supervisor/{{ project_name }}.conf · nginx/{{ project_name }}.conf
tests/
Makefile      常用开发命令
```

## 生产部署

1. `uv sync --frozen --no-dev` 并执行 `uv run alembic upgrade head`
2. 按环境修改 `deploy/supervisor/{{ project_name }}.conf`，由 supervisor 运行：

   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
   ```

3. 参考 `deploy/nginx/{{ project_name }}.conf` 配置反向代理
