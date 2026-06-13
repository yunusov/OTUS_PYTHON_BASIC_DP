from datetime import datetime

from src.core.dependencies import TaskRepo
from src.models import TaskOrm
from src.schemas import TaskCreate, TaskUpdate, TaskRead
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


class TaskService:

    sort_map = {
        "name": lambda p: p.name.lower(),
        "status": lambda p: p.status,
        "priority": lambda p: p.priority,
        "due_date": lambda p: p.due_date if p.due_date else datetime(2100, 1, 1),
    }

    def create(self, task_data: TaskCreate, repository: TaskRepo) -> TaskOrm:
        """Создать задачу"""
        task = TaskOrm(
            name=task_data.name,
            project_id=task_data.project_id,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            assignee_id=task_data.assignee_id,
            time_estimate=task_data.time_estimate,
            time_spent=task_data.time_spent,
            due_date=task_data.due_date,
            creator_id=task_data.creator_id,
        )
        repository.session.add(task)
        repository.session.commit()
        repository.session.refresh(task)
        return task

    def modify(
        self,
        task_id: int,
        task_data: TaskUpdate,
        repository: TaskRepo,
    ) -> TaskRead:
        """Изменение задачи (аналог ProjectService.modify)"""
        task_orm = repository.get_by_id(task_id)
        if task_orm is None:
            raise ValueError("Задача с таким ID не существует!")

        # Поля задачи, которые можно обновить
        fields_to_update = [
            "name",
            "description",
            "project_id",
            "status",
            "priority",
            "due_date",
            "assignee_id",
            "time_estimate",
            "time_spent",
        ]
        for field in fields_to_update:
            if hasattr(task_data, field):
                value = getattr(task_data, field)
                if value is not None:
                    setattr(task_orm, field, value)

        repository.save()
        logger.info(f"Task '{task_orm.id}' updated")
        return TaskRead.model_validate(task_orm, from_attributes=True)

    def delete(
        self,
        task_id: int,
        repository: TaskRepo,
    ) -> bool:
        """Удаление задачи (аналог ProjectService.delete)"""
        task_orm = repository.get_by_id(task_id)
        if not task_orm:
            return False
        repository.delete(task_orm)
        repository.save()
        return True

    def get_by_id(self, task_id: int, repository: TaskRepo) -> TaskRead | None:
        """Получить задачу по ID"""
        task_orm = repository.get_by_id(task_id)
        if task_orm is None:
            return None
        return TaskRead.model_validate(task_orm, from_attributes=True).model_copy(
            update={
                "creator": task_orm.creator.fullname if task_orm.creator else "",
                "assignee": task_orm.assignee.fullname if task_orm.assignee else "",
            }
        )

    def get_user_tasks(
        self,
        user_id: int,
        repository: TaskRepo,
        sort_by: str = "name",
        sort_dir: str = "desc",
    ) -> list[TaskRead]:
        """Получить все задачи пользователя (как создатель или исполнитель)"""
        tasks = repository.get_by_user(user_id)
        result = [
            TaskRead.model_validate(task, from_attributes=True).model_copy(
                update={
                    "creator": task.creator.fullname if task.creator else "",
                    "assignee": task.assignee.fullname if task.assignee else "",
                }
            )
            for task in tasks
        ]
        key_func = self.sort_map[sort_by]
        result.sort(key=key_func, reverse=(sort_dir == "desc"))
        return result

    def get_by_project_id(
        self,
        project_id: int,
        repository: TaskRepo,
        user_id: int | None,
        sort_by: str = "name",
        sort_dir: str = "desc",
    ) -> list[TaskRead]:
        tasks = repository.get_by_project(project_id, user_id)
        result = [
            TaskRead.model_validate(task, from_attributes=True).model_copy(
                update={
                    "creator": task.creator.fullname if task.creator else "",
                    "assignee": task.assignee.fullname if task.assignee else "",
                }
            )
            for task in tasks
        ]
        key_func = self.sort_map[sort_by]
        result.sort(key=key_func, reverse=(sort_dir == "desc"))
        return result

    def get_tasks_by_str(
        self,
        search_str: str,
        repository: TaskRepo,
        sort_by: str = "name",
        sort_dir: str = "desc",
    ) -> list[TaskRead]:
        """Получить все задачи пользователя (как создатель или исполнитель)"""
        tasks = repository.get_by_str(search_str)
        result = [
            TaskRead.model_validate(task, from_attributes=True).model_copy(
                update={
                    "creator": task.creator.fullname if task.creator else "",
                    "assignee": task.assignee.fullname if task.assignee else "",
                }
            )
            for task in tasks
        ]
        key_func = self.sort_map[sort_by]
        result.sort(key=key_func, reverse=(sort_dir == "desc"))
        return result
