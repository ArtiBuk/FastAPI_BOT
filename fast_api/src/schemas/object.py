from datetime import datetime
from typing import List

from pydantic import BaseModel

from database.enums import City, ObjectCategory


class ObjectIn(BaseModel):
    name: str
    description: str | None
    city: City
    category: ObjectCategory


class ObjectOut:
    class Short(BaseModel):
        name: str
        city: City
        description: str | None
        category: ObjectCategory

    class Full(Short):
        created_at: datetime
        updated_at: datetime
        deleted_at: datetime | None

    class WithCountReport(Short):
        id: int
        count_report: int | None

    class Config:
        orm_mode = True


class ObjectList(BaseModel):
    objects: List[ObjectOut.WithCountReport]


class ReportProfitOut(BaseModel):
    created_at: datetime
    revenue: float
    cost_price: float
    number_of_checks: int


class ReportProfitList(BaseModel):
    objects: ObjectOut.Short
    reports: List[ReportProfitOut] | None
