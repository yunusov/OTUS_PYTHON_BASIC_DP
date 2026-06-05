# src/schemas/task.py
from datetime import datetime
from enum import StrEnum, auto
from typing import Optional
from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
)
from src.schemas.user import UserRead


class TaskStatus(StrEnum):
    """Статусы задач"""

    TODO = auto()
    IN_PROGRESS = auto()
    DONE = auto()


class TaskPriority(StrEnum):
    """Приоритеты задач"""

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class TaskBase(BaseModel):
    """Схема для представления задачи в ответе"""

    name: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    creator_id: Optional[int] = None
    assignee_id: Optional[int] = None
    time_estimate: Optional[int] = None
    time_spent: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TaskRead(TaskBase):
    """Схема для чтения задачи с пользователем"""

    id: int
    created_at: datetime
    creator_id: int
    project_id: Optional[int] = None  # ← добавь явно
    assignee_id: Optional[int] = None  # ← добавь явно
    creator: Optional[UserRead] = None  # ← добавь
    assignee: Optional[UserRead] = None  # ← добавь

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

    @field_validator("assignee_id", "creator_id", mode="before")
    def convert_user_orm_to_int(cls, v):
        if isinstance(v, int):
            return v
        if hasattr(v, "id"):
            return v.id
        return v


class TaskCreate(TaskBase):
    """Схема для создания задачи"""

    creator_id: int


class TaskUpdate(TaskBase):
    """Схема для обновления задачи"""

    pass
