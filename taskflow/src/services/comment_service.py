from src.core.dependencies import CommentRepo, TaskRepo, UserRepo
from src.core.auth.user_manager import UserManager
from src.models import CommentOrm, UserOrm, TaskOrm
from src.schemas.comment import (
    CommentCreate,
    CommentRead,
    CommentUpdate,
)
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


class CommentService:

    async def create(
        self,
        comment_data: CommentCreate,
        repository: CommentRepo,
        user_manager: UserManager,
        tr: TaskRepo,
        ur: UserRepo,
    ) -> CommentRead:
        comment_orm = CommentOrm(**comment_data.model_dump())
        creator = repository.session.get(UserOrm, comment_data.creator_id)

        if creator is None:
            raise ValueError("Пользователь-создатель не найден")

        task = repository.session.get(TaskOrm, comment_data.task_id)
        if task is None:
            raise ValueError("Задача с таким ID не существует!")

        repository.create(comment_orm)
        repository.save()

        await user_manager.on_comment(comment_orm, tr, ur)
        return CommentRead.model_validate(comment_orm)

    def modify(
        self,
        comment_id: int,
        comment_data: CommentUpdate,
        repository: CommentRepo,
    ) -> CommentRead:
        comment_orm = repository.get_by_id(comment_id)
        if comment_orm is None:
            raise ValueError("Комментарий с таким ID не существует!")

        if comment_data.content is not None:
            comment_orm.content = comment_data.content

        if comment_data.task_id is not None:
            new_task = repository.session.get(TaskOrm, comment_data.task_id)
            if new_task is None:
                raise ValueError("Задача с таким ID не существует!")
            comment_orm.task_id = comment_data.task_id

        repository.save()
        return CommentRead.model_validate(comment_orm)

    def delete(
        self,
        comment_id: int,
        repository: CommentRepo,
    ) -> bool:
        comment_orm = repository.get_by_id(comment_id)
        if comment_orm is None:
            return False

        repository.delete(comment_orm)
        repository.save()
        return True

    def get_by_id(
        self,
        comment_id: int,
        repository: CommentRepo,
    ) -> CommentRead | None:
        comment = repository.get_by_id(comment_id)
        if comment is None:
            return None
        return CommentRead.model_validate(comment, from_attributes=True).model_copy(
            update={"creator": comment.creator.fullname if comment else ""}
        )

    def get_by_task_id(
        self,
        task_id: int,
        repository: CommentRepo,
    ) -> list[CommentRead]:
        comments = repository.get_by_task_id(task_id)
        return [
            CommentRead.model_validate(comment, from_attributes=True).model_copy(
                update={"creator": comment.creator.fullname if comment.creator else ""}
            )
            for comment in comments
        ]

    def get_user_comments(
        self, user_id: int, repository: CommentRepo
    ) -> list[CommentRead]:
        """Получить все комментарии пользователя"""
        comments = repository.get_by_creator_id(user_id)
        return [
            CommentRead.model_validate(comment, from_attributes=True).model_copy(
                update={"creator": comment.creator.fullname if comment.creator else ""}
            )
            for comment in comments
        ]
