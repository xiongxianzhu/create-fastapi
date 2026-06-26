<h1 align="center">{{ project_name }}</h1>

<p align="center">
  <sub>由 <a href="https://github.com/xiongxianzhu/create-fastapi">create-fastapi</a> 生成的 FastAPI 项目</sub>
</p>

<p align="center">
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/></a>
  <a href="https://www.uvicorn.org/"><img src="https://img.shields.io/badge/uvicorn-ASGI-4051B5?style=flat-square" alt="uvicorn"/></a>
  <a href="https://www.sqlalchemy.org/"><img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/></a>
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
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

健康检查 → `GET /api/v1/health` · 文档 → `/docs`

## 常用命令

| 场景 | 命令 |
|------|------|
| 开发 | `uv run uvicorn app.main:app --reload` |
| 迁移 | `uv run alembic revision --autogenerate -m "msg"` → `uv run alembic upgrade head` |
| 质量 | `uv run ruff check .` · `uv run mypy` · `uv run pytest` |
| 生产 | `uv sync --frozen --no-dev` → supervisor 拉起 uvicorn → nginx 反代 |
{% if use_celery %}| Worker | `uv run celery -A app.celery_app:celery_app worker -l info` |
{% endif %}{% if use_docker %}| 容器 | `docker compose up --build` |
{% endif %}

## 目录一览

```text
app/          main · core · db · api · models · schemas · services
alembic/      迁移
deploy/       supervisor/{{ project_name }}.conf · nginx/{{ project_name }}.conf
tests/
```

## 生产部署

1. `uv sync --frozen --no-dev` 并执行 `uv run alembic upgrade head`
2. 按环境修改 `deploy/supervisor/{{ project_name }}.conf`，由 supervisor 运行：

   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
   ```

3. 参考 `deploy/nginx/{{ project_name }}.conf` 配置反向代理
