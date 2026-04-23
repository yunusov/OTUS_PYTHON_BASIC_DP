from abc import ABCMeta, abstractmethod
from sqlalchemy.orm import Session

from src.core.database import BaseOrm


class BaseRepository:
    __metaclass__=ABCMeta

    def __init__(self, session: Session):
        self.session = session

    def save(self) -> None:
        '''Сохранить объект'''
        self.session.commit()    

    def create(self, entityOrm: BaseOrm) -> None:
        '''Создать объект'''
        self.session.add(entityOrm)

    def refresh(self, entityOrm: BaseOrm) -> None:
        '''Обновить объект'''
        self.session.refresh(entityOrm)

    @abstractmethod
    def get_by_id(self, user_id: int) -> BaseOrm | None:
        '''Объект по ИД'''

    def delete(self, entityOrm: BaseOrm) -> None:
        '''Удаление объекта'''
        self.session.delete(entityOrm)
