from sqlalchemy import select

from src.models import UserOrm
from src.utils.loguru_config import AppLogger
from .base import BaseRepository

logger = AppLogger().get_logger()


class UserRepository(BaseRepository):

    def get_by_id(self, user_id: int) -> UserOrm | None:
        '''Пользователь по ИД'''
        result = self.session.execute(
            select(UserOrm).where(UserOrm.id == user_id)
        )
        return result.scalar_one_or_none()

    def get_by_email(self, email: str) -> UserOrm | None:
        '''Пользователь по емейл'''
        result = self.session.execute(
            select(UserOrm).where(UserOrm.email == email)
        )
        return result.scalar_one_or_none()

    def get_by_username(self, username: str) -> UserOrm | None:
        '''Пользователь по логину'''
        result = self.session.execute(
            select(UserOrm).where(UserOrm.username == username)
        )
        return result.scalar_one_or_none()
    
