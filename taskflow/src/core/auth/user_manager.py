from typing import Optional, TYPE_CHECKING

from fastapi_cache import FastAPICache
from fastapi_users import (
    BaseUserManager,
    IntegerIDMixin,
)
from fastapi_users.db import BaseUserDatabase

from src.core.config import settings
from src.core.dependencies import TaskRepo, UserRepo
from src.mailing import (
    send_verification_email,
    send_confirmed_email,
    send_assigned_on_project_email,
    send_assigned_task_email,
    send_comment_email,
)
from src.models import (
    ProjectOrm,
    TaskOrm,
    UserOrm,
    CommentOrm,
)

# from utils.webhooks.user import send_new_user_notification
from src.utils.loguru_config import AppLogger

if TYPE_CHECKING:
    from fastapi import Request, BackgroundTasks
    from fastapi_users.password import PasswordHelperProtocol

logger = AppLogger().get_logger()


class UserManager(IntegerIDMixin, BaseUserManager[UserOrm, int]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    def __init__(
        self,
        user_db: BaseUserDatabase[UserOrm, int],
        password_helper: Optional["PasswordHelperProtocol"] = None,
        background_tasks: Optional["BackgroundTasks"] = None,
    ):
        super().__init__(user_db, password_helper)
        self.background_tasks = background_tasks

    async def on_after_register(
        self,
        user: UserOrm,
        request: Optional["Request"] = None,
    ):
        # if self.background_tasks:
        #     self.background_tasks.add_task(
        #         FastAPICache.clear,
        #         namespace=settings.cache.namespace.users_list,
        #     )
        # else:
        #     await FastAPICache.clear(
        #         namespace=settings.cache.namespace.users_list,
        #     )
        logger.warning(
            "User {} has registered.",
            user.id,
        )
        # await send_new_user_notification(user)

    async def on_after_forgot_password(
        self,
        user: UserOrm,
        token: str,
        request: Optional["Request"] = None,
    ):
        logger.warning(
            "User {} has forgot their password. Reset token: {}",
            user.id,
            token,
        )

    async def on_after_request_verify(
        self,
        user: UserOrm,
        token: str,
        request: Optional["Request"] = None,
    ):
        logger.warning(
            "Verification requested for user {}. Verification token: {}",
            user.id,
            token,
        )
        verification_link = request.url_for("verify_email").replace_query_params(
            token=token
        )
        self.background_tasks.add_task(
            send_verification_email,
            user=user,
            verification_link=str(verification_link),
            verification_token=token,
        )

    async def on_after_verify(
        self,
        user: UserOrm,
        request: Optional["Request"] = None,
    ):
        logger.warning(
            "User {} has been verified",
            user.id,
        )
        self.background_tasks.add_task(
            send_confirmed_email,
            user=user,
        )

    async def on_project_assign(
        self,
        users: list[UserOrm],
        project: ProjectOrm,
    ):
        for user in users:
            logger.warning(
                "User '{}' has been assigned on project '{}'",
                user.id,
                project.id,
            )
            self.background_tasks.add_task(
                send_assigned_on_project_email,
                user=user,
                project=project,
            )

    async def on_task_assign(
        self,
        task: TaskOrm,
    ):
        if task.assignee_id:
            user = await self.get(task.assignee_id)
            logger.warning(
                "Task '{}' has been assigned on user '{}'",
                task.id,
                user.id,
            )
            self.background_tasks.add_task(
                send_assigned_task_email,
                user=user,
                task=task,
            )

    async def on_comment(
        self,
        comment: CommentOrm,
        tr: TaskRepo,
        ur: UserRepo,
    ):
        task = tr.get_by_id(comment.task_id)
        users = ur.get_users_for_comment_email(comment.id, comment.creator_id)
        logger.warning(
            "Comment '{}' has been left on task {}",
            comment.id,
            task
        )
        if task:
            for user in users:
                self.background_tasks.add_task(
                    send_comment_email,
                    user=user,
                    task=task,
                    comment=comment,
                )
