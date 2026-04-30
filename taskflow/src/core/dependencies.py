from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

from src.repositories import UserRepository
from src.repositories.task_repository import TaskRepository      # ✅ ДОБАВЬ
from src.repositories.project_repository import ProjectRepository # ✅ ДОБАВЬ
from .database import session_factory

def get_db_session():
    session = session_factory()
    try:
        yield session
    finally:
        session.close()

DbSession = Annotated[Session, Depends(get_db_session)]

def get_user_repository(session: DbSession):
    return UserRepository(session)

UserRepo = Annotated[UserRepository, Depends(get_user_repository)]



def get_task_repository(session: DbSession):
    return TaskRepository(session)

TaskRepo = Annotated[TaskRepository, Depends(get_task_repository)]

def get_project_repository(session: DbSession):
    return ProjectRepository(session)

ProjectRepo = Annotated[ProjectRepository, Depends(get_project_repository)]  # ✅ ]