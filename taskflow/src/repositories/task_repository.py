from sqlalchemy import select
from sqlalchemy.orm import Session

from taskflow.src.models.task import TaskOrm
from taskflow.src.schemas.task import Task,TaskCreate,TaskUpdate


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, task: Task) -> TaskOrm:
        taskOrm = TaskOrm(**task.model_dump())
        self.session.add(taskOrm)
        self.session.commit()
        self.session.refresh(taskOrm)
        return taskOrm

    def get_by_id(self, task_id: int) -> TaskOrm | None:
        result = self.session.execute(select(TaskOrm).where(TaskOrm.id == task_id))
        return result.scalar_one_or_none()

    def get_by_project(self, project_id: int) -> list[TaskOrm]:
        result = self.session.execute(
            select(TaskOrm).where(TaskOrm.project_id == project_id)
        )
        return result.scalars().all()

    def update(self, task_id: int, task_data: TaskUpdate) -> TaskOrm | None:
        task_orm = self.get_by_id(task_id)
        if not task_orm:
            return None

        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task_orm, field, value)

        self.session.commit()
        self.session.refresh(task_orm)
        return task_orm

    def delete(self, task_id: int | None) -> bool:
        if task_id:
            task = self.get_by_id(task_id)
            if not task:
                return False
            self.session.delete(task)
            self.session.commit()
            return True
        return False