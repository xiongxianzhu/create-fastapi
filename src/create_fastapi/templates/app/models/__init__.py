"""ORM 模型包；导入模型以便 Alembic 侦测 metadata。"""

from app.db.base import Base, TimestampMixin

__all__ = ["Base", "TimestampMixin"]
