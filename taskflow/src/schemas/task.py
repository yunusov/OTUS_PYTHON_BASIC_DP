import datetime
from typing import Optional
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.models.task import TaskStatus, TaskPriority  # Импортируй Enum из модели


class Task(BaseModel):
    """Класс для представления сущности задача"""
    id: int
    name: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime.datetime] = None
    creator_id: int
    assignee_id: Optional[int] = None
    time_estimate: Optional[int] = None
    time_spent: Optional[int] = 0
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name")
    def check_name_len(cls, value):
        if len(value) > 255 or len(value) < 1:
            raise ValueError("Название задачи: 1-255 символов!")
        return value

    @field_validator("description")
    def check_description_len(cls, value):
        if value and len(value) > 1000:
            raise ValueError("Описание: max 1000 символов!")
        return value

    @field_validator("time_estimate", "time_spent")
    def check_time(cls, value):
        if value is not None and value < 0:
            raise ValueError("Время не может быть отрицательным!")
        return value


class TaskInDB(Task):
    """Для обновления в БД"""
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    @field_validator("time_spent")
    def check_time_spent(cls, value):
        if value is None or value >= 0:
            return value
        raise ValueError("Потраченное время не может быть отрицательным!")