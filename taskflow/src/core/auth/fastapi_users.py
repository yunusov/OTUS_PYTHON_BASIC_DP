from fastapi_users import FastAPIUsers

from src.models import UserOrm
from src.routers.api.dependencies.auth.user_manager import get_user_manager
from src.routers.api.dependencies.auth.backend import authentification_backend

fastapi_users = FastAPIUsers[UserOrm, int](
    get_user_manager,
    [authentification_backend]
)