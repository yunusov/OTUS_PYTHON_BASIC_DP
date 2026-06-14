import datetime
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class CommentBase(BaseModel):
    """Класс для представления сущности комментарий"""

    content: str | None = None
    task_id: int | None = None
    creator_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("content")
    def check_content_len(cls, value):
        content_len = len(value)
        if content_len > 1000 or content_len < 1:
            raise ValueError(
                "Содержимое комментария должно быть от 1 до 1000 символов!"
            )
        return value


class CommentRead(CommentBase):
    id: int
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    def __repr__(self) -> str:
        return "".join(
            [
                f"{self.__repr_name__()}(id={self.id},",
                f"content={self.content},",
                f"task_id={self.task_id},",
                f"creator_id={self.creator_id},",
                f"created_at={self.created_at})",
            ]
        )


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass
