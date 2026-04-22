from sqlalchemy.orm import (
    DeclarativeBase,
)

from src.models.mixins.int_id_pk import IntIdPkMixin

class BaseOrm(DeclarativeBase):
    pass