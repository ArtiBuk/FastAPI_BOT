from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, asc, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_db
from database.models import User, RightUser, Object, ReportProfit
from src.depends.authentication import get_current_user_request
from src.schemas.object import ObjectOut, ObjectList, ObjectIn, ReportProfitList, ReportProfitOut

router = APIRouter()


@router.get(
    "/object/all",
    response_model=ObjectList
)
async def get_all_objects(
        current_user: User = Depends(get_current_user_request),
        db_connect: AsyncSession = Depends(get_db)
):
    if current_user.right:
        obj_list = []
        subquery = (
            select(func.unnest(RightUser.object_access))
            .where(RightUser.id == current_user.right)
        ).as_scalar()

        query = (
            select(Object).where(Object.deleted_at == None)
            .where(Object.id.in_(subquery))
        )
        objects = (await db_connect.execute(query)).scalars().all()
        for obj in objects:
            query_count_report = (
                select(func.count())
                .where(ReportProfit.object == obj.id)
                .group_by(ReportProfit.object)
            )
            count = (await db_connect.execute(query_count_report)).scalar()
            obj_data = ObjectOut.WithCountReport(
                id=obj.id,
                name=obj.name,
                description=obj.description,
                city=obj.city,
                category=obj.category,
                count_report=count
            )
            obj_list.append(obj_data)
        return ObjectList(objects=obj_list)
    else:
        return ObjectList(objects=[])


@router.post(
    '/object/create',
    response_model=ObjectOut.Full
)
async def create_object(
        object_in: ObjectIn,
        current_user: User = Depends(get_current_user_request),
        db_connect: AsyncSession = Depends(get_db)
):
    try:
        if current_user.is_admin:
            object_data = object_in.dict()
            object_add = Object(**object_data)
            db_connect.add(object_add)
            await db_connect.flush()
            await db_connect.refresh(object_add)
            return ObjectOut.Full(
                created_at=object_add.created_at,
                updated_at=object_add.updated_at,
                deleted_at=object_add.deleted_at,
                id=object_add.id,
                name=object_add.name,
                city=object_add.city,
                category=object_add.category,
                description=object_add.description
            )

        else:
            raise HTTPException(403, detail="Нет прав создание объекта")
    except Exception as e:
        await db_connect.rollback()
        raise HTTPException(400, detail=str(e))


@router.get(
    "/object/{object_id}",
    response_model=ObjectOut.Full
)
async def get_object(
        object_id: int,
        current_user: User = Depends(get_current_user_request),
        db_connect: AsyncSession = Depends(get_db),
):
    if not current_user.is_admin:
        user_right: RightUser = (
            await db_connect.execute(select(RightUser).filter(RightUser.id == current_user.right))).scalar()
        if object_id not in user_right.object_access:
            raise HTTPException(403, detail="У вас нет прав на просмотр данного объекта")
    object_data: Object = (await db_connect.execute(select(Object).filter(Object.id == object_id))).scalar()
    if object_data is None:
        raise HTTPException(404, detail=f"Объекта с ID: {object_id} не существует")
    return ObjectOut.Full(
        created_at=object_data.created_at,
        updated_at=object_data.updated_at,
        deleted_at=object_data.deleted_at,
        id=object_data.id,
        name=object_data.name,
        city=object_data.city,
        category=object_data.category,
        description=object_data.description
    )


@router.delete(
    "/object/soft_removal",
)
async def soft_removal(
        object_id: int | None,
        current_user: User = Depends(get_current_user_request),
        db_connect: AsyncSession = Depends(get_db),
):
    if current_user.is_admin:
        object_data: Object = (await db_connect.execute(select(Object).filter(Object.id == object_id))).scalar()
        if object_data is None:
            raise HTTPException(404, detail="Объект не существует")
        if object_data.deleted_at:
            raise HTTPException(400, detail="Объект уже удален")
        object_data.deleted_at == datetime.now()
        return f"Объект {object_data.id} - {object_data.name}({object_data.city})удален"
    else:
        raise HTTPException(403, detail="Нет прав на удаление пользователя")


@router.get(
    "/object/{object_id}/report_profit",
    response_model=ReportProfitList
)
async def get_report_profit(
        object_id: int,
        current_user: User = Depends(get_current_user_request),
        db_connect: AsyncSession = Depends(get_db),
        date_start: datetime | None = None,
        date_end: datetime | None = None,
        sort_by_date: bool | None = True,
):
    if not current_user.is_admin:
        user_right: RightUser = (
            await db_connect.execute(select(RightUser).filter(RightUser.id == current_user.right))).scalar()
        if object_id not in user_right.object_access:
            raise HTTPException(403, detail="У вас нет прав на просмотр данного объекта")
    object_data: Object = (await db_connect.execute(select(Object).filter(Object.id == object_id))).scalar()
    query_count_report = (
        select(ReportProfit)
        .filter(ReportProfit.object == object_data.id)
    )
    if date_start and date_end:
        query_count_report = query_count_report.filter(
            and_(ReportProfit.created_at >= date_start, ReportProfit.created_at <= date_end))
    if sort_by_date is not None:
        if sort_by_date:
            query_count_report = query_count_report.order_by(asc(ReportProfit.created_at))
        else:
            query_count_report = query_count_report.order_by(desc(ReportProfit.created_at))
    reports_profit = (await db_connect.execute(query_count_report)).scalars().all()
    return ReportProfitList(
        objects=ObjectOut.Short(
            name=object_data.name,
            city=object_data.city,
            description=object_data.description,
            category=object_data.category
        ),
        reports=[ReportProfitOut(created_at=rep.created_at, revenue=rep.revenue, cost_price=rep.cost_price,
                                 number_of_checks=rep.number_of_checks) for rep in
                 reports_profit] if reports_profit else None
    )
