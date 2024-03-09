from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, asc, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_db
from database.models import User, Object, RightUser, ReportTimeControl
from src.depends.authentication import get_current_user_request
from src.schemas.object import ObjectOut
from src.schemas.user import UserOut, UserIn, RightOut, UserOutList, TimeControlOutList, TimeControlOut

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
        print(user_data)
        user_add = User(**user_data)
        db_connect.add(user_add)
        await db_connect.flush()
        await db_connect.refresh(user_add)
        return UserOut.Base(
            username=user_add.username,
            first_name=user_add.first_name,
            last_name=user_add.last_name,
            middle_name=user_add.middle_name,
            tg_id=user_add.tg_id,
            email=user_add.email,
            is_admin=user_add.is_admin,
            right=user_add.right if user_add.right else "Вам еще не выданы права администратором",
            time_work_start=user_add.time_work_start if user_add.time_work_start else None,
            time_work_end=user_add.time_work_end if user_add.time_work_end else None
        )
    except Exception as e:
        await db_connect.rollback()
        print(str(e))
        raise HTTPException(400, detail=str(e))


@router.get(
    "/user/me",
    response_model=UserOut.WithRight,
)
async def get_me(
        # requests: Request,
        current_user: User = Depends(get_current_user_request),
        db_connect: AsyncSession = Depends(get_db),
        tg_id_by_search: int | None = None

):
    if current_user.is_admin and tg_id_by_search:
        tg_id = tg_id_by_search
    else:
        tg_id = current_user.tg_id
    query_user = (
        select(User)
        .filter(User.tg_id == tg_id)
    )
    user: User = (await db_connect.execute(query_user)).scalar()

    if not user:
        raise HTTPException(404, detail="Пользователь не найден")
    if user.deleted_at:
        raise HTTPException(400, detail="Пользователь удален")
    if user.right:
        query_access_id = select(RightUser).filter(RightUser.id == user.right)
        right = (await db_connect.execute(query_access_id)).scalar()
        object_query = select(Object).filter(Object.id.in_(right.object_access))
        objects = (await db_connect.execute(object_query)).scalars().all()
    return UserOut.WithRight(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        tg_id=user.tg_id,
        email=user.email,
        is_admin=user.is_admin,
        right=user.right if user.right else None,
        access=RightOut.WithObject(
            id=right.id,
            name=right.name,
            description=right.description,
            object=[ObjectOut.Short(name=obj.name, city=obj.city, category=obj.category, description=obj.description)
                    for obj in
                    objects] if objects else None
        ) if user.right else None
    )


@router.put(
    "/user/update_me",
    response_model=UserOut.Base,
)
async def update_user_me(
        user_update: UserIn.UpdateMe,
        current_user: User = Depends(get_current_user_request),
):
    update_fields = {
        "first_name": user_update.first_name,
        "last_name": user_update.last_name,
        "middle_name": user_update.middle_name,
        "email": user_update.email,
    }
    for field, value in update_fields.items():
        if value is not None:
            setattr(current_user, field, value)

    current_user.updated_at = datetime.now()

    return UserOut.Base(
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        middle_name=current_user.middle_name,
        tg_id=current_user.tg_id,
        email=current_user.email,
        is_admin=current_user.is_admin,
        right=current_user.right if current_user.right else None,
    )


@router.put(
    "/user/update_by_admin",
    response_model=UserOut.Base,
)
async def update_by_admin(
        user_update: UserIn.UpdateAdmin,
        user_tg_id: int,
        current_user: User = Depends(get_current_user_request),
        db_connect: AsyncSession = Depends(get_db)

):
    if current_user.is_admin:
        user: User = (await db_connect.execute(select(User).filter(User.tg_id == user_tg_id))).scalar()
        update_fields = {
            "first_name": user_update.first_name,
            "last_name": user_update.last_name,
            "middle_name": user_update.middle_name,
            "email": user_update.email,
            "tg_id": user_update.tg_id,
            "is_admin": user_update.is_admin,
            "right": user_update.right,
            "username": user_update.username
        }

        for field, value in update_fields.items():
            if value is not None:
                setattr(user, field, value)

        user.updated_at = datetime.now()

        return UserOut.Base(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            tg_id=user.tg_id,
            email=user.email,
            is_admin=user.is_admin,
            right=user.right if user.right else None,
        )
    else:
        raise HTTPException(403, detail="Нет прав на редактирование пользователя")


@router.delete(
    "/user/soft_removal",
)
async def soft_removal(
        tg_id: int,
        current_user: User = Depends(get_current_user_request),
        db_connect: AsyncSession = Depends(get_db),
):
    if current_user.is_admin:
        user: User = (await db_connect.execute(select(User).filter(User.tg_id == tg_id))).scalar()
        if user is None:
            raise HTTPException(400, detail="Пользователь не существует")
        elif user.deleted_at:
            raise HTTPException(400, detail="Пользователь уже удален")
        else:
            user.deleted_at = datetime.now()
            return f"Пользователь {user.tg_id} - {user.first_name} {user.last_name} удален"
    else:
        raise HTTPException(403, detail="Нет прав на удаление пользователя")


@router.get(
    "/user/get_all",
    response_model=UserOutList,
)
async def get_all(
        with_right: bool | None = False,
        db_connect: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_request),
):
    if current_user.is_admin:
        query = select(User).filter(User.deleted_at == None)
        users: [User] = (await db_connect.execute(query)).scalars().all()

        user_out = []
        for user in users:
            user_data = UserOut.WithRight(
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                tg_id=user.tg_id,
                email=user.email,
                is_admin=user.is_admin,
                right=user.right if user.right else None,
                access=None
            )

            if with_right and user.right:
                user_right_query = select(RightUser).filter(RightUser.id == user.right)
                user_right: RightUser = (await db_connect.execute(user_right_query)).scalar()

                if user_right:
                    object_query = select(Object).filter(Object.id.in_(user_right.object_access))
                    objects: [Object] = (await db_connect.execute(object_query)).scalars().all()

                    user_data.access = RightOut.WithObject(
                        id=user_right.id,
                        name=user_right.name,
                        description=user_right.description,
                        object=[ObjectOut.Full(
                            id=obj.id,
                            name=obj.name,
                            city=obj.city,
                            category=obj.category,
                            description=obj.description,
                            created_at=obj.created_at,
                            updated_at=obj.updated_at,
                            deleted_at=obj.deleted_at
                        ) for obj in objects] if objects else None
                    )

            user_out.append(user_data)

        return UserOutList(users=user_out)

    else:
        raise HTTPException(403, detail="Нет прав на получение информации о пользователях")


@router.post(
    "/user/start_work",
)
async def start_work(
        is_started: bool | None = True,
        db_connect: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_request),
):
    try:
        if is_started:
            existing_record = (await db_connect.execute(select(ReportTimeControl).filter(
                (ReportTimeControl.user_id == current_user.id) & (
                        func.date(ReportTimeControl.data_start) == date.today())))).scalar()
            if existing_record:
                raise HTTPException(400, detail="Отметка о начале работы уже была сделана сегодня")
            time_control = ReportTimeControl(
                user_id=current_user.id,
                data_start=datetime.now()
            )
            db_connect.add(time_control)
            await db_connect.flush()
            return f"Отметка о начале работы зафиксирована в {datetime.now()}"
        else:
            existing_record = (await db_connect.execute(select(ReportTimeControl).filter(
                (ReportTimeControl.user_id == current_user.id) & (
                        func.date(ReportTimeControl.data_start) == date.today()) & (
                        func.date(ReportTimeControl.data_end) == date.today())))).scalar()
            if existing_record:
                raise HTTPException(400, detail="Отметка о конце работы уже была сделана сегодня")
            time_control: ReportTimeControl = (await db_connect.execute(
                select(ReportTimeControl).filter(func.date(ReportTimeControl.created_at) == date.today()))).scalar()
            if not time_control:
                raise HTTPException(400, detail="Вы еще не создали запись о начале работы")
            time_control.data_end = datetime.now()
            time_difference = time_control.data_end - time_control.data_start
            time_control.working_hours = int(time_difference.total_seconds() / 60)
            return f"Отметка о конце работы зафиксирована в {time_control.data_end}. Время работы составило -  {time_control.working_hours // 60} часов, {(time_control.working_hours % 60):02d} минут"
    except Exception as e:
        await db_connect.rollback()
        raise HTTPException(400, detail=str(e))


@router.get(
    "/user/get_time_control",
    response_model=TimeControlOutList
)
async def get_time_control(
        db_connect: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_request),
        date_start: datetime | None = None,
        date_end: datetime | None = None,
        sort_by_date: bool | None = True,
        tg_id_by_search: int | None = None

):
    if current_user.is_admin and tg_id_by_search:
        tg_id = tg_id_by_search
    else:
        tg_id = current_user.tg_id
    user_id = (await db_connect.execute(select(User.id).filter(User.tg_id == tg_id))).scalar()

    if not user_id:
        raise HTTPException(404, detail="Пользователь не найден")
    query = select(ReportTimeControl).filter(ReportTimeControl.user_id == user_id)

    if date_start and date_end:
        query = query.filter(and_(ReportTimeControl.created_at >= date_start, ReportTimeControl.created_at <= date_end))

    if sort_by_date is not None:
        if sort_by_date:
            query = query.order_by(asc(ReportTimeControl.created_at))
        else:
            query = query.order_by(desc(ReportTimeControl.created_at))

    report = (await db_connect.execute(query)).scalars().all()
    return TimeControlOutList(
        reports=[TimeControlOut(date_start=rep.data_start, date_end=rep.data_end, working_hours=rep.working_hours) for
                 rep in report] if report else None)
