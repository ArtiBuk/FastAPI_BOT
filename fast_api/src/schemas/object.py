from pydantic import BaseModel

from database.enums import City, ObjectCategory


class ObjectOut:

    class Short(BaseModel):
        name: str
        city: City
        category: ObjectCategory

        class Config:
            orm_mode = True