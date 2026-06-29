"""generator 单元测试。"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from create_fastapi.generator import (
    GenerationError,
    ProjectOptions,
    _is_git_url,
    generate_project,
    resolve_template,
    validate_name,
)

PLACEHOLDER_RE = re.compile(r"\{\{|\{%")


def _read_all_text(root: Path) -> dict[Path, str]:
    out: dict[Path, str] = {}
    for p in root.rglob("*"):
        if p.is_file():
            try:
                out[p.relative_to(root)] = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pass
    return out


def test_validate_name_rejects_invalid() -> None:
    for bad in ["My-App", "my_app", "1app", "my app", "my.app", ""]:
        with pytest.raises(GenerationError):
            validate_name(bad)


def test_validate_name_accepts_valid() -> None:
    for ok in ["myapp", "my-api", "my-api-backend", "app2"]:
        validate_name(ok)


def test_base_generation(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    result = generate_project(ProjectOptions(name="my-api", target_dir=target))

    assert result.file_count > 0
    assert (target / "app" / "main.py").exists()
    assert (target / "pyproject.toml").exists()
    assert (target / ".env.example").exists()
    assert (target / ".python-version").exists()
    assert (target / ".gitignore").exists()
    assert (target / "alembic" / "env.py").exists()
    assert (target / "Makefile").exists()
    assert (target / "deploy" / "supervisor" / "my-api.conf").exists()
    assert (target / "deploy" / "nginx" / "my-api.conf").exists()
    assert (target / "logs" / ".gitkeep").exists()

    assert not (target / "celeryconfig.py").exists()
    assert not (target / "app" / "tasks").exists()
    assert not (target / "app" / "core" / "redis.py").exists()
    assert not (target / "Dockerfile").exists()

    for rel, text in _read_all_text(target).items():
        assert not PLACEHOLDER_RE.search(text), f"占位符残留：{rel}"


def test_pyproject_name_substituted(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    generate_project(ProjectOptions(name="my-api", target_dir=target))
    content = (target / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "my-api"' in content
    assert "fastapi[standard]>=" in content
    assert "uvicorn[standard]>=" in content
    assert "pydantic-settings" in content
    assert "sqlmodel>=" in content
    assert "greenlet>=" in content
    assert "sqlalchemy[asyncio]" not in content
    assert "redis" not in content
    assert "celery" not in content


def test_no_flask_deps(tmp_path: Path) -> None:
    target = tmp_path / "pureapi"
    generate_project(ProjectOptions(name="pureapi", target_dir=target))
    joined = "\n".join(_read_all_text(target).values())
    for forbidden in ["flask", "flask_restful", "marshmallow"]:
        assert forbidden not in joined.lower(), f"不应依赖 {forbidden}"
    health = (target / "app" / "api" / "v1" / "endpoints" / "health.py").read_text(
        encoding="utf-8"
    )
    assert "APIRouter" in health


def test_sqlmodel_stack(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    generate_project(ProjectOptions(name="my-api", target_dir=target))
    alembic_env = (target / "alembic" / "env.py").read_text(encoding="utf-8")
    assert "SQLModel.metadata" in alembic_env
    deps = (target / "app" / "api" / "deps.py").read_text(encoding="utf-8")
    assert "SessionDep" in deps
    assert "sqlmodel" in deps
    assert not (target / "app" / "db" / "base.py").exists()


def test_supervisor_uses_uvicorn(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    generate_project(ProjectOptions(name="my-api", target_dir=target))
    conf = (target / "deploy" / "supervisor" / "my-api.conf").read_text(encoding="utf-8")
    assert "uvicorn app.main:app" in conf
    assert "gunicorn" not in conf


def test_redis_module(tmp_path: Path) -> None:
    target = tmp_path / "app1"
    generate_project(ProjectOptions(name="app1", target_dir=target, use_redis=True))
    assert (target / "app" / "core" / "redis.py").exists()
    main_py = (target / "app" / "main.py").read_text(encoding="utf-8")
    assert "redis_client" in main_py
    assert "REDIS_URL" in (target / ".env.example").read_text(encoding="utf-8")
    pyproject = (target / "pyproject.toml").read_text(encoding="utf-8")
    assert "redis>=" in pyproject
    assert not (target / "celeryconfig.py").exists()


def test_celery_module(tmp_path: Path) -> None:
    target = tmp_path / "app2"
    generate_project(
        ProjectOptions(name="app2", target_dir=target, use_redis=True, use_celery=True)
    )
    assert (target / "celeryconfig.py").exists()
    assert (target / "app" / "celery_app.py").exists()
    assert (target / "app" / "tasks" / "example.py").exists()
    pyproject = (target / "pyproject.toml").read_text(encoding="utf-8")
    assert "celery[redis]" in pyproject
    conf = (target / "deploy" / "supervisor" / "app2.conf").read_text(encoding="utf-8")
    assert "celery -A app.celery_app:celery_app" in conf


def test_docker_module(tmp_path: Path) -> None:
    target = tmp_path / "app3"
    generate_project(ProjectOptions(name="app3", target_dir=target, use_docker=True))
    assert (target / "Dockerfile").exists()
    assert (target / "docker-compose.yml").exists()
    assert (target / ".dockerignore").exists()
    dockerfile = (target / "Dockerfile").read_text(encoding="utf-8")
    assert "uvicorn" in dockerfile
    assert "gunicorn" not in dockerfile


def test_docker_compose_includes_services_when_celery(tmp_path: Path) -> None:
    target = tmp_path / "app4"
    generate_project(
        ProjectOptions(
            name="app4",
            target_dir=target,
            use_redis=True,
            use_celery=True,
            use_docker=True,
        )
    )
    compose = (target / "docker-compose.yml").read_text(encoding="utf-8")
    assert "redis:" in compose
    assert "worker:" in compose
    assert "db:" in compose


def test_is_git_url() -> None:
    for url in [
        "https://github.com/u/repo",
        "http://example.com/x",
        "git@github.com:u/repo.git",
        "ssh://git@host/u/repo",
        "git://host/u/repo",
        "./local.git",
    ]:
        assert _is_git_url(url)
    for path in ["./my-template", "/abs/path", "templates", "~/t"]:
        assert not _is_git_url(path)


def test_resolve_builtin_template() -> None:
    with resolve_template(None) as tdir:
        assert (tdir / "app" / "main.py").exists()


def test_resolve_local_template_missing() -> None:
    with pytest.raises(GenerationError):
        with resolve_template("/no/such/template/dir"):
            pass


def test_custom_local_template(tmp_path: Path) -> None:
    tpl = tmp_path / "tpl"
    (tpl / "app").mkdir(parents=True)
    (tpl / "README.md").write_text(
        "# {{ project_name }}\npkg={{ package_name }}\n", encoding="utf-8"
    )
    (tpl / "app" / "main.py").write_text(
        "NAME = '{{ project_name }}'\n{% if use_redis %}REDIS = True\n{% endif %}",
        encoding="utf-8",
    )
    (tpl / "Dockerfile").write_text("FROM python:3.13\n", encoding="utf-8")

    target = tmp_path / "out"
    with resolve_template(str(tpl)) as tdir:
        result = generate_project(
            ProjectOptions(name="cool-app", target_dir=target, template_dir=tdir)
        )

    assert result.file_count > 0
    readme = (target / "README.md").read_text(encoding="utf-8")
    assert "# cool-app" in readme
    assert "pkg=cool_app" in readme
    assert not (target / "Dockerfile").exists()
    assert "REDIS" not in (target / "app" / "main.py").read_text(encoding="utf-8")


def test_path_placeholder_in_filename(tmp_path: Path) -> None:
    tpl = tmp_path / "tpl"
    conf_dir = tpl / "deploy" / "supervisor"
    conf_dir.mkdir(parents=True)
    conf_path = conf_dir / "{{ project_name }}.conf"
    conf_path.write_text("[program:{{ project_name }}]\n", encoding="utf-8")

    target = tmp_path / "out"
    generate_project(ProjectOptions(name="my-api", target_dir=target, template_dir=tpl))

    assert (target / "deploy" / "supervisor" / "my-api.conf").exists()
    content = (target / "deploy" / "supervisor" / "my-api.conf").read_text(encoding="utf-8")
    assert "[program:my-api]" in content


def test_custom_local_template_skips_git_dir(tmp_path: Path) -> None:
    tpl = tmp_path / "tpl"
    (tpl / ".git").mkdir(parents=True)
    (tpl / ".git" / "config").write_text("[core]\n", encoding="utf-8")
    (tpl / "file.txt").write_text("{{ project_name }}\n", encoding="utf-8")

    target = tmp_path / "out"
    generate_project(ProjectOptions(name="x", target_dir=target, template_dir=tpl))
    assert (target / "file.txt").exists()
    assert not (target / ".git").exists()


def test_overwrite_protection(tmp_path: Path) -> None:
    target = tmp_path / "app5"
    generate_project(ProjectOptions(name="app5", target_dir=target))
    marker = target / "app" / "main.py"
    marker.write_text("# user edit\n", encoding="utf-8")

    result = generate_project(ProjectOptions(name="app5", target_dir=target))
    assert any(p.name == "main.py" for p in result.skipped)
    assert marker.read_text(encoding="utf-8") == "# user edit\n"

    result2 = generate_project(ProjectOptions(name="app5", target_dir=target, force=True))
    assert any(p.name == "main.py" for p in result2.created)
    assert "create_app" in marker.read_text(encoding="utf-8")
