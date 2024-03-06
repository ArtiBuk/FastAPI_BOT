from fastapi import Header, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from core.session import get_db
from database.models import User


async def auth_tg(
        tg_id: str = Header(...),
        db_connect: AsyncSession = Depends(get_db)
) -> User:
    tg_id = int(tg_id)
    user: User = (await db_connect.execute(select(User).filter(User.tg_id == tg_id))).scalar()
    if user is None or user.deleted_at:
        raise HTTPException(401, detail="Пользователя по такому ID не существует")


async def get_current_user(
        tg_id: str = Header(...),
        db_connect: AsyncSession = Depends(get_db)
) -> User:
    tg_id = int(tg_id)
    user: User = (await db_connect.execute(select(User).filter(User.tg_id == tg_id))).scalar()
    if user is None or user.deleted_at:
        raise HTTPException(401, detail="Пользователя по такому ID не существует")
    return user


async def get_current_user_request(
        requests: Request,
        db_connect: AsyncSession = Depends(get_db)
) -> User:
    tg_id = int(requests.headers.get('tg_id'))
    user: User = (await db_connect.execute(select(User).filter(User.tg_id == tg_id))).scalar()
    if user is None or user.deleted_at:
        raise HTTPException(401, detail="Пользователя по такому ID не существует")
    return user
