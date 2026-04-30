from datetime import datetime
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class TaskStatus(StrEnum):
    """Статусы задач"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(StrEnum):
    """Приоритеты задач"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(BaseModel):
    """Схема для представления задачи в ответе (с id и created_at)."""
    id: int
    name: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    creator_id: int
    assignee_id: Optional[int] = None
    time_estimate: Optional[int] = None
    time_spent: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name")
    @classmethod
    def check_name_len(cls, v: str) -> str:
        if len(v) > 255 or len(v) < 3:
            raise ValueError("Название задачи от 3 до 255 символов")
        return v

    @field_validator("description")
    @classmethod
    def check_description_len(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 1000:
            raise ValueError("Описание задачи не более 1000 символов")
        return v

    @field_validator("time_estimate", "time_spent")
    @classmethod
    def check_time_values(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Время не может быть отрицательным")
        return v


class TaskInDB(Task):
    """Схема для создания задач в БД."""

    def __repr__(self) -> str:
        return "".join(
            [
                f"{self.__repr_name__()}(id={self.id},",
                f"name={self.name},",
                f"project_id={self.project_id},",
                f"status={self.status},",
                f"priority={self.priority},",
                f"creator_id={self.creator_id})",
            ]
        )
