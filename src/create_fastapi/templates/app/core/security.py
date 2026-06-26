"""鉴权依赖占位，可按业务扩展 JWT / API Key。"""

from __future__ import annotations

from fastapi import Header, HTTPException, status


async def admin_required(x_admin_token: str | None = Header(default=None)) -> None:
    """管理端鉴权占位：生产环境请替换为真实校验逻辑。"""
    if not x_admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少管理端凭证",
        )
