from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.core import settings
from src.core.auth.fastapi_users import fastapi_users
from src.models import UserOrm
from src.schemas import (
    UserRead,
    UserUpdate,
)
from src.routers.api.dependencies.auth.user_manager import get_user_manager
from fastapi_users import exceptions
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode, ErrorModel

router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"],
)

get_current_active_user = fastapi_users.current_user(active=True)
get_current_superuser = fastapi_users.current_user(active=True, superuser=True)


async def get_user_or_404(
    id: str,
    user_manager: BaseUserManager[UserOrm, int] = Depends(get_user_manager),
) -> UserOrm:
    try:
        parsed_id = user_manager.parse_id(id)
        return await user_manager.get(parsed_id)
    except (exceptions.UserNotExists, exceptions.InvalidID) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


# /me
@router.get(
    "/me",
    response_model=UserRead,
    name="users:current_user",
)
async def me(
    user: UserOrm = Depends(get_current_active_user),
):
    return UserRead.model_validate(user)


@router.patch(
    "/me",
    response_model=UserRead,
    name="users:patch_current_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {
                                "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                    "at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_me(
    request: Request,
    user_update: UserUpdate,  # type: ignore
    user: UserOrm = Depends(get_current_active_user),
    user_manager: BaseUserManager[UserOrm, int] = Depends(get_user_manager),
):
    try:
        user = await user_manager.update(
            user_update, user, safe=True, request=request
        )
        return UserRead.model_validate(user)
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
        )


# /{id}
@router.get(
    "/{id}",
    response_model=UserRead,
    name="users:user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
    },
)
async def get_user(
    user: UserOrm = Depends(get_user_or_404),
    current_user: UserOrm = Depends(get_current_active_user),
):
    return UserRead.model_validate(user)


@router.patch(
    "/{id}",
    response_model=UserRead,
    dependencies=[Depends(get_current_superuser)],
    name="users:patch_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {
                                "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                    "at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_user(
    user_update: UserUpdate,  # type: ignore
    request: Request,
    user: UserOrm = Depends(get_user_or_404),
    user_manager: BaseUserManager[UserOrm, int] = Depends(get_user_manager),
):
    try:
        user = await user_manager.update(
            user_update, user, safe=False, request=request
        )
        return UserRead.model_validate(user)
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_superuser)],
    name="users:delete_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
    },
)
async def delete_user(
    request: Request,
    user: UserOrm = Depends(get_user_or_404),
    user_manager: BaseUserManager[UserOrm, int] = Depends(get_user_manager),
):
    await user_manager.delete(user, request=request)
    return None