from src.core.dependencies import TaskRepo
from src.models import TaskOrm
from src.schemas.task import Task, TaskInDB
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


class TaskService:

    def create(
            self,
            task_data: TaskInDB,
            repository: TaskRepo,
    ) -> Task:
        """Создание задачи"""
        task_orm = TaskOrm(task_data)  # ← как ProjectOrm(project_data)
        repository.create(task_orm)
        repository.save()
        repository.refresh(task_orm)
        logger.info(f"Task {task_orm.id} created")
        return Task.model_validate(task_orm)

    def modify(
            self,
            task_data: TaskInDB,
            repository: TaskRepo,
    ) -> Task:
        """Изменение задачи (аналог ProjectService.modify)"""
        task_id = task_data.id
        if not task_id:
            raise ValueError("ID задачи не указан!")

        task_orm = repository.get_by_id(task_id)
        if task_orm is None:
            raise ValueError("Задача с таким ID не существует!")

        # Поля задачи, которые можно обновить
        fields_to_update = [
            "name", "description", "project_id", "status", "priority",
            "due_date", "creator_id", "assignee_id", "time_estimate", "time_spent"
        ]
        for field in fields_to_update:
            if hasattr(task_data, field):
                setattr(task_orm, field, getattr(task_data, field))

        repository.save()
        repository.refresh(task_orm)
        logger.info(f"Task {task_orm.id} updated")
        return Task.model_validate(task_orm)

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
