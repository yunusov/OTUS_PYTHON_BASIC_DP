from src.core.dependencies import TaskRepo
from src.models import TaskOrm
from src.schemas import TaskCreate, TaskUpdate, TaskRead
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


class TaskService:

    def create(
            self,
            task_data: TaskCreate,
            repository: TaskRepo,
    ) -> TaskRead:
        """Создание задачи"""
        task_orm = TaskOrm(**task_data.model_dump())
        repository.create(task_orm)
        repository.save()
        logger.info(f"Task {task_orm.id} created")
        return TaskRead.model_validate(task_orm)

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
            "name", "description", "project_id", "status", "priority",
            "due_date", "creator_id", "assignee_id", "time_estimate", "time_spent"
        ]
        for field in fields_to_update:
            if hasattr(task_data, field):
                value = getattr(task_data, field)
                old_value = getattr(task_orm, field)
                setattr(task_orm, field, value if value else old_value)

        repository.save()
        logger.info(f"Task {task_orm.id} updated")
        return TaskRead.model_validate(task_orm)

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
