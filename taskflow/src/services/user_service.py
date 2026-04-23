from src.core.dependencies import UserRepo
from src.schemas import User, UserInDB
from src.core.security import hash_password


class UserService:

    def modify(
        self,
        user_data: UserInDB,
        repository: UserRepo,
    ) -> User:
        """Изменение данных пользователя"""
        userOrm = repository.get_by_id(user_data.id)
        if userOrm is None:
            raise ValueError("Пользователь с таким ID не существует!")
        userOrm.username = user_data.username
        userOrm.fullname = user_data.fullname
        userOrm.email = user_data.email
        userOrm.is_active = user_data.is_active
        userOrm.hashed_password = hash_password(user_data.hashed_password)
        repository.save()
        return User.model_validate(userOrm)

    def delete(
        self,
        user_id: int,
        repository: UserRepo,
    ) -> bool:
        """Удаления пользователя"""
        userOrm = repository.get_by_id(user_id)
        if userOrm:
            repository.delete(userOrm)
            repository.save()
            return True
        return False
