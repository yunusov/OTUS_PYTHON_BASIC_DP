import datetime
from fastapi_users import schemas
from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
)


class UserBase:
    """Класс для представления сущности пользователь"""
    username: str | None = None
    fullname: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("username")
    def check_username_len(cls, value):
        username_len = len(value)
        if username_len > 32 or username_len < 3:
            raise ValueError("Логин должен быть от 3 до 32 символов в длину!")
        return value

    @field_validator("fullname")
    def check_fullname_len(cls, value):
        username_len = len(value)
        if username_len > 100:
            raise ValueError(
                "Полное имя пользователя должно быть менее 100 символов в длину!"
            )
        return value

    @field_validator("email")
    def check_email_len(cls, value):
        username_len = len(value)
        if username_len > 50:
            raise ValueError("Email должно быть менее 50 символов в длину!")
        return value

    def __repr__(self) -> str:
        return self.fullname or ""


class UserRead(schemas.BaseUser[int], UserBase):
    """Класс для представления сущности пользователь для чтения"""
    created_at: datetime.datetime
    updated_at: datetime.datetime

class UserReadSimple(BaseModel):
    id: int
    fullname: str = ""
    assigned_project: int | None = None
    model_config = ConfigDict(from_attributes=True)

class UserCreate(schemas.BaseUserCreate, UserBase):

    @field_validator("password")
    def check_password_len(cls, value):
        if not value:
            raise ValueError("Пароль не должен быть пустым!")
        return value


class UserUpdate(schemas.BaseUserUpdate, UserBase):
    pass


class UserRegisteredNotification(BaseModel):
    user: UserRead
    ts: int
