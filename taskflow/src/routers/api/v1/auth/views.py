from fastapi import APIRouter
from fastapi.security import HTTPBasic

from src.core.dependencies import UserRepo
from src.schemas import User, UserInDB
from src.services import AuthService, UserService
from src.utils.loguru_config import AppLogger

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = AppLogger().get_logger()

security = HTTPBasic()


@router.post("/register")
def register_user(
    user: UserInDB,
    repository: UserRepo,
) -> User:
    """Создать пользователя"""
    return AuthService().register(user, repository)


@router.put("/register")
def modify_user(
    user: UserInDB,
    repository: UserRepo,
) -> User | None:
    """Модифицировать пользователя"""
    return UserService().modify(user, repository)


@router.delete("/register/{user_id}")
def remove_user(user_id: int, repository: UserRepo) -> bool:
    """Удалить пользователя"""
    return UserService().delete(user_id, repository)


@router.post("/")
def auth_user(user: UserInDB, repository: UserRepo) -> User | None:
    """Аутенцифицировать пользователя"""
    return AuthService().authenticate(
        user.username,
        user.hashed_password,
        repository,
    )


# @router.get("/register")
# def basic_auth_credentials(
#     credentials: Annotated[HTTPBasicCredentials, Depends(security)],
# ):
#     return {
#         "message": "Hi!",
#         "username": credentials.username,
#         "password": credentials.password,
#     }


@router.post("/logout")
def logout_user():
    """Logout пользователя"""

    return {
        "message": "Hi!",
    }
