from sqlalchemy import CheckConstraint, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import BaseOrm, created_at


class UserOrm(BaseOrm):

    __tablename__ = "tf_users"

    fullname: Mapped[str] = mapped_column(
        Text,
        default="",
        server_default="",
    )
    username: Mapped[str] = mapped_column(Text, unique=True)
    email: Mapped[str] = mapped_column(
        Text,
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
    )
