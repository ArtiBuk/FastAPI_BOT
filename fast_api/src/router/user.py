from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select, cast, ARRAY, Integer, func, literal, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_db
from database.models import User, Object, RightUser
from src.depends.authentication import get_current_user, auth_tg
from src.schemas.object import ObjectOut
from src.schemas.user import UserOut, UserIn, RightOut

router = APIRouter()


@router.post(
    "/user/create",
    response_model=UserOut.Base
)
async def create_user(
        user_in: UserIn.Create,
        db_connect: AsyncSession = Depends(get_db),
):
    try:
        user_data = user_in.dict()
        user_add = User(**user_data)
        db_connect.add(user_add)
        await db_connect.flush()
        await db_connect.refresh(user_add)
        return UserOut(
            username=user_add.username,
            first_name=user_add.first_name,
            last_name=user_add.last_name,
            middle_name=user_add.middle_name,
            tg_id=user_add.tg_id,
            email=user_add.email,
        )
    except Exception as e:
        await db_connect.rollback()
        raise HTTPException(400, detail=str(e))


@router.get(
    "/user/me",
    response_model=UserOut.WithRight,
    dependencies=[Depends(auth_tg)]
)
async def get_me(
        current_user: User = Depends(get_current_user),
        db_connect: AsyncSession = Depends(get_db),
):
    if current_user.right:
        query_right = (
            select(User.right)
            .filter(User.id == current_user.id)
        )
        right_user_id = (await db_connect.execute(query_right)).scalar()
        query_access_id = select(RightUser).filter(RightUser.id == right_user_id)
        right = (await db_connect.execute(query_access_id)).scalar()
        object_query = select(Object).filter(Object.id.in_(right.object_access))
        objects = (await db_connect.execute(object_query)).scalars().all()
    return UserOut.WithRight(
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        middle_name=current_user.middle_name,
        tg_id=current_user.tg_id,
        email=current_user.email,
        is_admin=current_user.is_admin,
        right=current_user.right,
        access=RightOut(
            id=right.id,
            name=right.name,
            description=right.description,
            object=[ObjectOut.Short(name=obj.name, city=obj.city, category=obj.category) for obj in
                    objects] if objects else None
        ) if current_user.right else "Вам еще не выданы права доступа"
    )


@router.put(
    "/user/update_me",
    response_model=UserOut.Base,
    dependencies=[Depends(auth_tg)]
)
async def update_user_me(
        user_update: UserIn.UpdateMe,
        current_user: User = Depends(get_current_user),
):
    if user_update.first_name:
        current_user.first_name = user_update.first_name
    elif user_update.last_name:
        current_user.last_name = user_update.last_name
    elif user_update.middle_name:
        current_user.middle_name = user_update.middle_name
    elif user_update.email:
        current_user.email = user_update.email
    current_user.updated_at = datetime.now()

    return UserOut.Base(
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        middle_name=current_user.middle_name,
        tg_id=current_user.tg_id,
        email=current_user.email,
        is_admin=current_user.is_admin,
        right=current_user.right
    )


@router.put(
    "/user/update_by_admin",
    response_model=UserOut.Base,
    dependencies=[Depends(auth_tg)]
)
async def update_by_admin(
        user_update: UserIn.UpdateAdmin,
        current_user: User = Depends(get_current_user),
):
    if current_user.is_admin:
        if user_update.first_name:
            current_user.first_name = user_update.first_name
        elif user_update.last_name:
            current_user.last_name = user_update.last_name
        elif user_update.middle_name:
            current_user.middle_name = user_update.middle_name
        elif user_update.email:
            current_user.email = user_update.email
        elif user_update.tg_id:
            current_user.tg = user_update.tg_id
        elif user_update.is_admin:
            current_user.is_admin = user_update.is_admin
        elif user_update.right:
            current_user.right = user_update.right
        current_user.updated_at = datetime.now()

        return UserOut.Base(
            username=current_user.username,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            middle_name=current_user.middle_name,
            tg_id=current_user.tg_id,
            email=current_user.email,
            is_admin=current_user.is_admin,
            right=current_user.right
        )
    else:
        raise HTTPException(403, detail="Нет прав на редактирование пользователя")


@router.delete(
    "/user/soft_removal",
    dependencies=[Depends(auth_tg)]
)
async def soft_removal(
        tg_id: int,
        current_user: User = Depends(get_current_user),
        db_connect: AsyncSession = Depends(get_db),
):
    if current_user.is_admin:
        user: User = (await db_connect.execute(select(User).filter(User.tg_id == tg_id))).scalar()
        if user is None:
            raise HTTPException(400, detail="Пользователь не существует")
        if user.deleted_at:
            raise HTTPException(400, detail="Пользователь уже удален")
        user.deleted_at == datetime.now()
        return f"Пользователь {user.tg_id} - {user.first_name} {user.last_name} удален"
    else:
        raise HTTPException(403, detail="Нет прав на удаление пользователя")

