from typing import Iterable

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.auth import get_current_user
from app.db.session import get_session


async def require_role_in(roles: Iterable[str], user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    rid = user.role_id or 0
    res = await session.execute(text("SELECT role_name FROM roles WHERE role_id=:rid"), {"rid": rid})
    row = res.first()
    role_name = (row[0] if row else None) or ""
    if role_name not in set(roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    return user


async def require_perm_codes(perms: Iterable[str], user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    rid = user.role_id or 0
    res = await session.execute(
        text(
            """
            SELECT p.perm_code FROM role_permissions rp
            JOIN permissions p ON rp.perm_id = p.perm_id
            WHERE rp.role_id = :rid
            """
        ),
        {"rid": rid},
    )
    user_perms = {row[0] for row in res.all()}
    need = set(perms)
    if not need.issubset(user_perms):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    return user

