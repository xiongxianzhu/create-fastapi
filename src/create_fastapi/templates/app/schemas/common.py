"""API 入参/出参（SQLModel，不含 table=True）。"""

from __future__ import annotations

from sqlmodel import SQLModel


class ExampleCreate(SQLModel):
    name: str


class ExampleRead(SQLModel):
    id: int
    name: str
