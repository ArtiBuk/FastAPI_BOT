import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Column, String, Integer, Enum, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON, JSONB
from sqlalchemy.orm import relationship

from database.enums import City, ObjectCategory

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

metadata = sa.MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)

NOW_AT_UTC = sa.text("timezone('utc', now())")


class TimestampMixin:
    """
    Миксин для добавления временных меток создания и обновления записи.

    Атрибуты:
    ----------
    :param created_at: время создания записи.
    :type datetime.datetime
    :param updated_at: время обновления записи.
    :type datetime.datetime
    """

    created_at = Column(
        sa.TIMESTAMP(timezone=False), server_default=NOW_AT_UTC, nullable=False
    )
    updated_at = Column(
        sa.TIMESTAMP(timezone=False),
        server_default=NOW_AT_UTC,
        nullable=False,
        onupdate=NOW_AT_UTC,
    )


class SoftDeleteMixin:
    """
    Миксин для добавления пометки об удалении записи.

    Атрибуты:
    ----------
    :param deleted_at: время удаления записи.
    :type datetime.datetime
    """

    deleted_at = Column(sa.TIMESTAMP(timezone=False), nullable=True, index=True)


class User(TimestampMixin, SoftDeleteMixin, Base):
    """
        Модель пользователя

        Таблица: users
    """
    __tablename__ = "users"
    id: uuid.UUID = sa.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()")
    )
    username: str = sa.Column(String, unique=True, nullable=False)
    first_name: str = sa.Column(String, nullable=False)
    last_name: str = sa.Column(String, nullable=False)
    middle_name: str = sa.Column(String, nullable=True)
    tg_id: int = sa.Column(Integer, unique=True, nullable=False)
    email: str = sa.Column(String, unique=True, nullable=False)
    is_admin: bool = sa.Column(Boolean, default=False, nullable=False)
    right: uuid.UUID = sa.Column(
        UUID,
        ForeignKey("right_user.id"),
        nullable=True,
    )


class Object(TimestampMixin, SoftDeleteMixin, Base):
    """
        Модель объектов

        Таблица: objects
    """
    __tablename__ = "objects"

    id: int = sa.Column(Integer, primary_key=True, autoincrement=True)
    name: str = sa.Column(String, nullable=False)
    description: str = sa.Column(String, nullable=True)
    city: City = sa.Column(Enum(City), nullable=False)
    category: ObjectCategory = sa.Column(Enum(ObjectCategory), nullable=False)


class RightUser(TimestampMixin, SoftDeleteMixin, Base):
    """
        Модель определяющая права пользователей

        Таблица: right_user
    """
    __tablename__ = "right_user"

    id: uuid.UUID = sa.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()")
    )
    name: str = sa.Column(String, unique=True, nullable=False)
    description: str = sa.Column(String, nullable=True)
    object_access = sa.Column(ARRAY(Integer), nullable=False, info={"description": "К каким объектом есть доступ"})


class ReportProfit(TimestampMixin, SoftDeleteMixin, Base):
    """
        Модель для хранения данных для отчетов о выручке

        Таблица: report_profit
    """
    __tablename__ = "report_profit"

    id: int = sa.Column(Integer, primary_key=True, autoincrement=True)
    object: int = sa.Column(
        Integer,
        ForeignKey("objects.id"),
        nullable=False
    )
    revenue: float = sa.Column(Float, nullable=False, info={"description": "Данные о выручке"})
    cost_price: float = sa.Column(Float, nullable=False, info={"description": "Данные о себестоимости"})
    number_of_checks = sa.Column(Integer, nullable=False, info={"description": "Данные о кол-ве чеков"})


class ReportTimeControl(TimestampMixin, SoftDeleteMixin, Base):
    """
        Модель для хранения данных для отчетов о времени работы сотрудника

        Таблица: report_profit
    """
    __tablename__ = "report_time_control"

    id: int = sa.Column(Integer, primary_key=True, autoincrement=True)
    user_id: uuid.UUID = sa.Column(
        UUID,
        ForeignKey("users.id"),
        nullable=False,
        info={"description": "К какому сотруднику относиться отчет"}
    )
    data_start: datetime = sa.Column(DateTime, nullable=False, info={"description": "Время начала работы"})
    data_end: datetime = sa.Column(DateTime, nullable=True, info={"description": "Время конца работы"})
    working_hours: int = sa.Column(Integer, nullable=True, info={"description": "Итоговое время в минутах"})
