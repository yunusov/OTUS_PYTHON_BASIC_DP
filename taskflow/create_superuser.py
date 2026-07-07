import asyncio
from src.core.database import get_db_helper
from src.models.user import UserOrm
from src.core.security import hash_password
from sqlalchemy import select, func


async def create_superuser():
    db_helper = get_db_helper()

    async for session in db_helper.get_session():
        stmt = select(UserOrm).where(UserOrm.username == "admin")
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("⚠️ Суперпользователь уже существует!")
            return

        user = UserOrm(
            username="admin",
            fullname="Admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            is_active=True,
            is_superuser=True,
            is_verified=True,
            created_at=func.now(),
            updated_at=func.now(),
        )
        session.add(user)
        await session.commit()
        print("✅ Суперпользователь создан!")
        print(f"👤 Логин: admin")
        print(f"👤 Имя: Admin")
        print(f"📧 Почта: admin@example.com")
        print(f"🔑 Пароль: admin123")


if __name__ == "__main__":
    asyncio.run(create_superuser())
