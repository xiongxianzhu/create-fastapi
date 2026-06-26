<p align="center">
  <strong>create-fastapi · Agent 指南</strong>
</p>

<p align="center">
  <sub>Typer CLI 脚手架 · 只生成文件，不代跑 <code>uv sync</code> / 迁移 / 启动</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/CLI-Typer-009485?style=flat-square" alt="Typer"/>
  <img src="https://img.shields.io/badge/模板-Jinja2-B41717?style=flat-square" alt="Jinja2"/>
  <img src="https://img.shields.io/badge/产物-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
</p>

---

## 仓库是什么

| 层级 | 路径 | 职责 |
|------|------|------|
| **工具** | `src/create_fastapi/` | CLI、模板渲染、模块门控 |
| **模板** | `src/create_fastapi/templates/` | 生成项目的 Jinja2 源文件 |
| **测试** | `tests/` | 生成逻辑单元测试 |
| **需求** | `docs/prd-create-fastapi.md` | PRD，行为以之为准 |

改生成结果 → 编辑 **templates**；改 CLI 行为 → 编辑 **cli.py / generator.py**。

## 关键约束

- 运行时依赖仅 **Typer + Jinja2**
- 生成项目：**FastAPI + async SQLAlchemy 2.0 + Alembic + uvicorn**（不用 gunicorn 默认模板）
- 可选模块：`--redis` / `--celery` / `--docker`，通过 `CELERY_PATHS` / `REDIS_PATHS` / `DOCKER_PATHS` 门控
- 占位变量：`{{ project_name }}`、`{{ package_name }}`、`use_redis`、`use_celery`、`use_docker`
- **不得**在 CLI 内执行 `uv sync`、迁移或服务启动

## 常用命令

```bash
# 工具仓库
uv sync
uv run pytest
uv run ruff check .
uv run mypy
uv run create-fastapi my-api --path /tmp -y

# 验证生成项目（示例）
cd /tmp/my-api && uv sync && uv run pytest
```

## 修改检查清单

- [ ] 模板变更后跑 `uv run pytest`
- [ ] 新增门控路径同步更新 `generator.py` 中的集合
- [ ] 占位符不得残留（测试会校验 `{{` / `{%`）
- [ ] 根 README 与 `templates/README.md` 保持口径一致

## Git 约定

| 项 | 规范 |
|----|------|
| 分支 | `feat/` · `fix/` · `docs/` |
| 提交 | Conventional Commits，**简体中文**描述 |
| 类型 | `feat` `fix` `docs` `test` `refactor` `chore` 等 |

详见 `.cursor/rules/git-workflow.mdc`。

## 参考

- 姊妹项目：[create-flask](https://github.com/xiongxianzhu/create-flask)
- 用户文档：[README.md](README.md)
