"""SQLModel 表模型；导入以确保 Alembic 侦测 metadata。"""

from sqlmodel import SQLModel

from app.models.base import TimestampMixin

__all__ = ["SQLModel", "TimestampMixin"]
