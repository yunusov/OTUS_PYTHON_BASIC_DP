from sqlalchemy import and_, select, or_
from sqlalchemy.orm import joinedload

from src.models import TaskOrm
from src.schemas import TaskStatus
from src.utils.loguru_config import AppLogger
from .base import BaseRepository

logger = AppLogger().get_logger()


class TaskRepository(BaseRepository):

    def get_by_user(self, user_id: int) -> list[TaskOrm]:
        """Все задачи пользователя (как создатель или исполнитель)"""
        result = self.session.execute(
            select(TaskOrm)
            .options(joinedload(TaskOrm.assignee))
            .options(joinedload(TaskOrm.creator, innerjoin=True))
            .where(or_(TaskOrm.creator_id == user_id, TaskOrm.assignee_id == user_id))
        )
        return list(result.scalars().all())

    def get_by_project(
        self, project_id: int, user_id: int | None = None
    ) -> list[TaskOrm]:
        """Задачи проекта"""
        logger.info(f"project_id: {project_id}, user_id: {user_id}")
        query = (
            select(TaskOrm)
            .options(joinedload(TaskOrm.assignee))
            .options(joinedload(TaskOrm.creator, innerjoin=True))
            .where(TaskOrm.project_id == project_id)
        )
        if user_id:
            query = query.where(
                and_(
                    TaskOrm.project_id == project_id,
                    or_(TaskOrm.creator_id == user_id, TaskOrm.assignee_id == user_id),
                )
            )
        result = self.session.execute(query)
        return list(result.scalars().all())

    def get_by_assignee(self, assignee_id: int) -> list[TaskOrm]:
        """Задачи исполнителя"""
        result = self.session.execute(
            select(TaskOrm).where(TaskOrm.assignee_id == assignee_id)
        )
        return list(result.scalars().all())

    def get_by_id(self, id: int) -> TaskOrm | None:
        """Получить задачу по ID"""
        result = self.session.execute(
            select(TaskOrm)
            .options(joinedload(TaskOrm.assignee))
            .options(joinedload(TaskOrm.creator, innerjoin=True))
            .where(TaskOrm.id == id),
        )
        return result.scalar_one_or_none()

    def get_by_str(self, search_str: str) -> list[TaskOrm]:
        """Задачи по строке"""
        result = self.session.execute(
            select(TaskOrm)
            .options(joinedload(TaskOrm.assignee, innerjoin=True))
            .options(joinedload(TaskOrm.creator, innerjoin=True))
            .where(TaskOrm.name.contains(search_str))
        )
        return list(result.scalars().all())

    def update_task_status(self, task: TaskOrm, status: TaskStatus) -> None:
        """Обновить статус задачи"""
        if not task:
            logger.error(f"Task with id {task_id} not found")
            raise ValueError(f"Task with id {task_id} not found")
        task.status = status

    def update_task_status(self, task: TaskOrm, status: TaskStatus) -> None:
        """Обновить статус задачи"""
        if not task:
            logger.error(f"Task with id {task_id} not found")
            raise ValueError(f"Task with id {task_id} not found")
        task.status = status

    def get_completed_tasks_since(
        self, since_date: datetime, user_id: int | None = None
    ) -> list[TaskOrm]:
        """
        Получить завершенные задачи с указанной даты
        """
        from datetime import datetime  # локальный импорт, если не импортирован вверху

        query = (
            select(TaskOrm)
            .options(joinedload(TaskOrm.assignee))
            .options(joinedload(TaskOrm.creator))
            .options(joinedload(TaskOrm.project))
            .where(
                TaskOrm.status == TaskStatus.DONE, TaskOrm.completed_at >= since_date
            )
        )

        if user_id:
            query = query.where(
                or_(TaskOrm.creator_id == user_id, TaskOrm.assignee_id == user_id)
            )

        result = self.session.execute(query)
        return list(result.scalars().all())

    def get_overdue_tasks(self, user_id: int | None = None) -> list[TaskOrm]:
        """
        Получить просроченные задачи
        """
        from datetime import datetime

        query = (
            select(TaskOrm)
            .options(joinedload(TaskOrm.assignee))
            .options(joinedload(TaskOrm.creator))
            .where(TaskOrm.due_date < datetime.now(), TaskOrm.status != TaskStatus.DONE)
        )

        if user_id:
            query = query.where(
                or_(TaskOrm.creator_id == user_id, TaskOrm.assignee_id == user_id)
            )

        result = self.session.execute(query)
        return list(result.scalars().all())
