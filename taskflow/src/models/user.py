from sqlalchemy import CheckConstraint, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import BaseOrm, created_at
from src.schemas.user import User


class UserOrm(BaseOrm):

    __tablename__ = "tf_users"

    def __init__(self, user: User):
        super().__init__(
            fullname=user.fullname,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
        )

    fullname: Mapped[str] = mapped_column(
        Text,
        default="",
        server_default="",
    )
    username: Mapped[str] = mapped_column(Text, unique=True)
    email: Mapped[str] = mapped_column(
        Text,
        unique=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        Text,
    )
    created_at: Mapped[created_at]
    is_active: Mapped[bool]

    __table_args__ = (
        CheckConstraint(
            func.length(username) <= 32,
            name="username_max_length",
        ),
        CheckConstraint(
            func.length(fullname) <= 100,
            name="full_name_max_length",
        ),
        CheckConstraint(
            func.length(email) <= 50,
            name="email_max_length",
        ),
    )
