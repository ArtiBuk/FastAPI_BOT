import uuid
from typing import List

from pydantic import BaseModel, EmailStr

from src.schemas.object import ObjectOut


class RightOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    object: List[ObjectOut.Short] | None


class UserIn:
    class Create(BaseModel):
        username: str
        first_name: str
        last_name: str
        middle_name: str | None
        tg_id: int
        email: EmailStr

    class UpdateMe(BaseModel):
        first_name: str | None
        last_name: str | None
        middle_name: str | None
        email: EmailStr | None

    class UpdateAdmin(BaseModel):
        username: str | None
        first_name: str | None
        last_name: str | None
        middle_name: str | None
        tg_id: int | None
        email: EmailStr | None
        is_admin: bool | None
        right: uuid.UUID | None


class UserOut(BaseModel):
    class Base(BaseModel):
        username: str
        first_name: str
        last_name: str
        middle_name: str | None
        tg_id: int
        email: EmailStr
        is_admin: bool
        right: uuid.UUID | str

    class WithRight(Base):
        access: RightOut

    class Config:
        orm_mode = True
