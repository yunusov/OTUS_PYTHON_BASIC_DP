import datetime
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime as DT


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    project_id: Optional[int] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[DT] = None
    creator_id: int
    assignee_id: Optional[int] = None
    time_estimate: Optional[int] = Field(None, ge=0)
    time_spent: Optional[int] = Field(0, ge=0)


class TaskCreate(TaskBase):
    """Схема для создания задачи"""


class TaskUpdate(BaseModel):
    """Схема для обновления задачи"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    project_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[DT] = None
    assignee_id: Optional[int] = None
    time_estimate: Optional[int] = Field(None, ge=0)
    time_spent: Optional[int] = Field(None, ge=0)


class Task(TaskBase):
    """Полная схема задачи"""
    id: Optional[int] = None
    created_at: DT = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    updated_at: DT = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))

    model_config = ConfigDict(from_attributes=True)


class TaskOut(Task):
    """Схема для ответа API"""
    pass