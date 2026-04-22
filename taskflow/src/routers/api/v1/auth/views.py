from fastapi import APIRouter
from fastapi.security import HTTPBasic

from src.utils.loguru_config import AppLogger
from src.schemas.user import User
from src.core.dependencies import UserRepo

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = AppLogger().get_logger()

security = HTTPBasic()


@router.post("/register")
def register_user(
    user: User,
    repository: UserRepo,
) -> User:
    """Создать пользователя"""
    user = User(
        id=None,
        username=user.username,
        fullname=user.fullname,
        email=user.email,
        hashed_password=user.hashed_password,
        is_active=True,
    )
    userOrm = repository.create(user)
    return User.model_validate(userOrm)


@router.put("/register")
def modify_user(
    user: User,
    repository: UserRepo,
) -> User | None:
    """Создать пользователя"""
    user = User(
        id=user.id,
        username=user.username,
        fullname=user.fullname,
        email=user.email,
        hashed_password=user.hashed_password,
        is_active=user.is_active,
    )
    repository.update(user)

    return user


@router.delete("/register/{user_id}")
def remove_user(user_id: int, repository: UserRepo) -> bool:
    return repository.delete(user_id)


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
