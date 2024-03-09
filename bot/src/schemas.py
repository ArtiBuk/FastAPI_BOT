from pydantic import BaseModel, EmailStr


class UserCreateApi(BaseModel):
    username: str
    first_name: str
    last_name: str
    middle_name: str | None
    tg_id: int
    email: EmailStr


class UpdateForAdminApi(BaseModel):
    username: str | None
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    tg_id: None
    email: EmailStr | None
    is_admin: bool | None
    right: None


class UpdateUserApi(BaseModel):
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    email: EmailStr | None


class ObjectCreateApi(BaseModel):
    name: str
    description: str | None
    city: str
    category: str
