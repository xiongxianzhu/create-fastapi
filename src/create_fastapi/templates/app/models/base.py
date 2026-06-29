"""SQLModel 公共 mixin 与基类约定。"""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """公共时间戳字段（供 `table=True` 模型继承）。"""

    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
