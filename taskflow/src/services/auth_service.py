from src.core.dependencies import UserRepo
from src.core.security import verify_password
from src.schemas import User, UserInDB
from src.models import UserOrm


class AuthService:
    def register(
        self,
        user_data: UserInDB,
        repository: UserRepo,
    ) -> User:
        """Регистрация пользователя"""
        existing_email = repository.get_by_email(user_data.email)
        existing_username = repository.get_by_username(user_data.username)
        if existing_email or existing_username:
            raise ValueError("Пользователь с таким емейлом или именем уже зарегистрирован!")
        userOrm = UserOrm(user_data)
        repository.create(userOrm)
        repository.save()
        return User.model_validate(userOrm)

    def authenticate(
        self,
        username: str,
        password: str,
        repository: UserRepo,
    ) -> User | None:
        """Аутентификация пользователя"""
        userOrm = repository.get_by_username(username)
        if not userOrm:
            return None
        if not verify_password(password, userOrm.hashed_password):
            return None
        return User.model_validate(userOrm)
