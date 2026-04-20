from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, Notification

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    # Проверяем, есть ли пользователь в таблице users
    if message.from_user is None:
        await message.answer("Не удалось определить пользователя.")
        return
    user = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = user.scalar_one_or_none()
    if not user:
        new_user = User(telegram_id=message.from_user.id)
        session.add(new_user)
        await session.commit()
        await message.answer("Вы подписаны на уведомления!")
    else:
        await message.answer("Вы уже в базе. Бот работает.")


@router.message(Command("my_notifications"))
async def cmd_my_notifications(message: Message, session: AsyncSession):
    # Пример получения непрочитанных уведомлений (is_sent = False)
    if message.from_user is None:
        await message.answer("Не удалось определить пользователя.")
        return
    result = await session.execute(
        select(Notification).where(
            Notification.user_telegram_id == message.from_user.id,
            Notification.is_sent == False
        ).order_by(Notification.created_at)
    )
    notifs = result.scalars().all()
    if not notifs:
        await message.answer("Новых уведомлений нет.")
        return

    for notif in notifs:
        await message.answer(f"🔔 {notif.message_text}")
        # Помечаем как отправленное
        notif.is_sent = True  # type: ignore
    await session.commit()
