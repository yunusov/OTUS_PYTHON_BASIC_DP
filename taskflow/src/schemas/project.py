import datetime
from enum import StrEnum, auto
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class ProjectType(StrEnum):
    SOFTWARE = auto()
    BUSINESS = auto()
    SERVICE_DESK = auto()


class ProjectBase(BaseModel):
    """Класс для представления сущности проект"""

    name: str | None = None
    description: str | None = None
    project_type: ProjectType | None = None
    creator_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name")
    def check_name_len(cls, value):
        name_len = len(value)
        if name_len > 100 or name_len < 3:
            raise ValueError("Название проекта должно быть от 3 до 100 символов!")
        return value

    @field_validator("description")
    def check_description_len(cls, value):
        if len(value) > 1000:
            raise ValueError("Описание проекта не более 1000 символов!")
        return value

    @field_validator("project_type", mode="before")
    def normalize_project_type(cls, value: str) -> str:
        mapping = {
            "BUSINESS"     : "business",
            "SERVICE_DESK" : "service_desk",
            "SOFTWARE"     : "software",
        }
        return mapping.get(value.upper(), value.lower())


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    def __repr__(self) -> str:
        return "".join(
            [
                f"{self.__repr_name__()}(id={self.id},",
                f"name={self.name},",
                f"description={self.description},",
                f"project_type={self.project_type},",
                f"creator_id={self.creator_id},",
                f"created_at={self.created_at})",
            ]
        )


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass
