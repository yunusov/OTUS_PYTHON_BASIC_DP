import secrets

from fastapi import Request
from sqladmin import ModelView

from .converter import ModelConverter
from src.models import AccessTokenOrm


class AccessTokenAdmin(ModelView, model=AccessTokenOrm):
    column_list = [
        AccessTokenOrm.token,
        AccessTokenOrm.created_at,
        AccessTokenOrm.user,
    ]
    form_converter = ModelConverter
    column_default_sort = [
        (AccessTokenOrm.created_at, True),
    ]
    form_include_pk = True
    name = "Access Token"
    can_edit = False
    page_size = 50

    form_create_rules = [
        "user",
    ]

    def insert_model(
        self,
        request: Request,
        data: dict,
    ):
        if "token" not in data:
            data.update(token=secrets.token_urlsafe())
        return super().insert_model(
            request=request,
            data=data,
        )
