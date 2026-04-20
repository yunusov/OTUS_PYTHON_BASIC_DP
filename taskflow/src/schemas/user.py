import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class User(BaseModel):
    """Класс для представления сущности пользователь"""

    id: int | None
    username: str
    fullname: str
    email: EmailStr
    hashed_password: str
    is_active: bool
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

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

    @field_validator("hashed_password")
    def check_hashed_password_len(cls, value):
        if not value:
            raise ValueError("Пароль не должен быть пустым!")
        return value
