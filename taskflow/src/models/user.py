from sqlalchemy import CheckConstraint, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import BaseOrm, created_at
from src.core.security import hash_password
from src.schemas import UserInDB


class UserOrm(BaseOrm):

    __tablename__ = "tf_users"

    def __init__(self, user: UserInDB):
        super().__init__(
            fullname=user.fullname,
            username=user.username,
            email=user.email,
            hashed_password=hash_password(user.hashed_password),
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

    def __repr__(self) -> str:
        return "".join(
            [
                f"UserOrm(id={self.id},",
                f"username={self.username},",
                f"fullname={self.fullname},",
                f"email={self.email},",
                f"is_active={self.is_active},",
                f"created_at={self.created_at})",
            ]
        )

    created_at: Mapped[created_at]
    is_active: Mapped[bool]

    project: Mapped[list["ProjectOrm"]] = relationship(back_populates="creator")

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
