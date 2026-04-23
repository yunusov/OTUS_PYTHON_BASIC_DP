from sqlalchemy import select
from sqlalchemy.orm import Session

from taskflow.src.models.user import UserOrm
from taskflow.src.schemas.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> UserOrm:
        userOrm = UserOrm(user)
        self.session.add(userOrm)
        self.session.commit()
        self.session.refresh(userOrm)
        return userOrm

    def get_by_id(self, user_id: int) -> UserOrm | None:
        result = self.session.execute(select(UserOrm).where(UserOrm.id == user_id))
        return result.scalar_one_or_none()

    def update(self, user: User) -> UserOrm | None:
        query = select(UserOrm).filter_by(id=user.id)
        userOrm = self.session.execute(query).scalar_one_or_none()
        if userOrm:
            userOrm.username = user.username
            userOrm.fullname = user.fullname
            userOrm.email = user.email
            userOrm.is_active = user.is_active
            userOrm.hashed_password = user.hashed_password

            self.session.commit()
            self.session.refresh(userOrm)
        return userOrm

    def delete(self, user_id: int | None) -> bool:
        if user_id:
            user = self.get_by_id(user_id)
            if not user:
                return False
            self.session.delete(user)
            self.session.commit()
            return True
        return False
