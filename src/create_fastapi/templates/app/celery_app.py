"""Celery 应用实例。"""

from __future__ import annotations

from celery import Celery

celery_app = Celery("{{ project_name }}")
celery_app.config_from_object("celeryconfig")
celery_app.autodiscover_tasks(["app.tasks"])
