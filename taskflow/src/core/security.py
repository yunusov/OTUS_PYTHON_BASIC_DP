import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль пользователя"""
    return bcrypt.checkpw(
        password=plain_password.encode("utf-8"),
        hashed_password=hashed_password.encode("utf-8"),
    )


def hash_password(password: str) -> str:
    """Хэшировать пароль пользователя"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")
