# create-fastapi · Agent 指南

Typer CLI 脚手架，只生成文件，不代跑 `uv sync`、迁移或启动服务。

## 沟通

- 默认使用简体中文回复和编写文档。
- 先说明结果，再补充必要的操作与限制。
- 保持表达简洁，避免重复说明和无关扩展。

### 回答前的澄清流程

处理用户提出的问题时，不直接给出最终答案。先向用户说明：

1. 问题中没有明确说出、但已默认成立的假设。
2. 仍缺少的关键信息，以及这些信息可能如何改变答案。
3. 人们处理这类问题时最常犯的一个错误。

## Git

- 提交信息采用 Conventional Commits，例如 `feat(auth): 添加路由守卫`。
- 提交描述默认使用简体中文。
- 只暂存当前任务相关文件；提交前检查暂存内容，不得夹带日志、构建产物、编辑器文件或敏感信息。
- 不得对 `.gitignore` 忽略的目录或文件执行 `git add`；忽略规则只防未被追踪的文件，显式 `add` 会绕过忽略。
- 用户明确调用 `git-commit` Skill 时，提交当前任务相关改动后推送当前分支。
- 当前分支没有上游时，将上游设置为 `origin` 的同名分支后推送。
- 没有可提交改动但存在未推送提交时，只执行推送，不创建空提交。
- 提交失败时不继续推送；推送失败时保留本地提交，并报告失败原因和当前状态。
- 禁止强制推送、覆盖远端历史或暂存无关文件来规避失败。

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
- 生成项目：**Python 3.14+** · FastAPI 0.138+（`[standard]`）· SQLModel 0.0.39+ async · Alembic · uvicorn 0.49+（`[standard]`）
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

| 项目 | 说明 |
|------|------|
| [create-flask](https://github.com/xiongxianzhu/create-flask) | 姊妹 CLI 脚手架 |
| [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) | FastAPI 官方全栈模板，后端模式可借鉴 |
| [sqlmodel](https://github.com/fastapi/sqlmodel) | FastAPI 官方 ORM，本模板默认数据层 |
| [README.md](README.md) | 用户文档 |
