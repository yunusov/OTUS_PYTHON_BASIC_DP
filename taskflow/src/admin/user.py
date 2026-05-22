from fastapi import Request
from fastapi_users.password import PasswordHelper
from sqladmin import ModelView

from src.admin.converter import ModelConverter
from src.models import UserOrm
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()

password_helper = PasswordHelper()


class UserAdmin(ModelView, model=UserOrm):
    column_list = [
        UserOrm.id,
        UserOrm.email,
        UserOrm.is_active,
        UserOrm.is_superuser,
        UserOrm.is_verified,
    ]
    details_template = "custom_details.html"
    form_converter = ModelConverter
    form_include_pk = False
    column_labels = {
        UserOrm.hashed_password: "password",
        UserOrm.created_at: "created",
        UserOrm.updated_at: "updated",
    }
    column_default_sort = [
        (UserOrm.email, False),
    ]
    name = "User"
    page_size = 50
    form_excluded_columns = [
        UserOrm.access_tokens,
        UserOrm.created_tasks,
        UserOrm.project,
        UserOrm.user_projects,
        UserOrm.created_at,
        UserOrm.updated_at,
    ]
    column_details_exclude_list = [
        UserOrm.user_projects,
    ]

    async def on_model_change(
        self,
        data: dict,
        model: UserOrm,
        is_created: bool,
        request: Request,
    ) -> None:
        raw_password = data.get("hashed_password") or password_helper.generate()
        if is_created or model.hashed_password != raw_password:
            data.update(
                hashed_password=password_helper.hash(raw_password),
            )
