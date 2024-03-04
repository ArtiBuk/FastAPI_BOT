from fastapi import Header, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_db
from database.models import User


async def auth_tg(
        tg_id: int = Header(...),
        db_connect: AsyncSession = Depends(get_db)
) -> User:
    user: User = (await db_connect.execute(select(User).filter(User.tg_id == tg_id))).scalar()
    if user is None or user.deleted_at:
        raise HTTPException(401, detail="Пользователя по такому ID не существует")


async def get_current_user(
        tg_id: int = Header(...),
        db_connect: AsyncSession = Depends(get_db)
) -> User:
    user: User = (await db_connect.execute(select(User).filter(User.tg_id == tg_id))).scalar()
    if user is None or user.deleted_at:
        raise HTTPException(401, detail="Пользователя по такому ID не существует")
    return user
