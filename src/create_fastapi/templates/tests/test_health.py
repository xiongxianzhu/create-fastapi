"""健康检查冒烟测试。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    from app.main import app

    return TestClient(app)


def test_health_ok(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_admin_health_requires_token(client: TestClient) -> None:
    resp = client.get("/api/admin/v1/health")
    assert resp.status_code == 401


def test_admin_health_ok(client: TestClient) -> None:
    resp = client.get("/api/admin/v1/health", headers={"X-Admin-Token": "test-token"})
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
