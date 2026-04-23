import datetime
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectType(StrEnum):
    SOFTWARE = "software"
    BUSINESS = "business"
    SERVICE_DESK = "service_desk"


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(default="", max_length=1000)
    creator_id: int
    project_type: ProjectType = ProjectType.SOFTWARE


class ProjectCreate(ProjectBase):
    """Схема для создания проекта"""


class ProjectUpdate(BaseModel):
    """Схема для обновления проекта"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    project_type: Optional[ProjectType] = None
    creator_id: Optional[int] = None


class Project(ProjectBase):
    """Полная схема проекта с ID и timestamps"""
    id: Optional[int] = None
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    model_config = ConfigDict(from_attributes=True)


class ProjectOut(Project):
    """Схема для ответа API (с creator данными при необходимости)"""
    pass