import datetime
from typing import Optional
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectType(StrEnum):
    SOFTWARE = "software"
    BUSINESS = "business"
    SERVICE_DESK = "service_desk"


class Project(BaseModel):
    id: int | None = None
    name: str
    description: Optional[str] = None
    creator_id: int
    project_type: ProjectType
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name")
    def check_name_len(cls, value):
        if len(value) < 3 or len(value) > 100:
            raise ValueError("Название проекта: 3–100 символов!")
        return value

    @field_validator("description")
    def check_description_len(cls, value):
        if value is not None and len(value) > 1000:
            raise ValueError("Описание: максимум 1000 символов!")
        return value