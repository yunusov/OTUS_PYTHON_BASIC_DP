from .user import UserOrm
from .project import ProjectOrm
from .task import TaskOrm

from sqlalchemy.orm import configure_mappers

configure_mappers()

__all__ = ["ProjectOrm", "UserOrm", "TaskOrm"]
