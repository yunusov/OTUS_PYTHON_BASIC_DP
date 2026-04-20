import asyncio
import os
from aiogram import Bot
from sqlalchemy import select, update
from database import AsyncSessionLocal
from models import Notification


async def check_and_send_notifications(bot: Bot):
    while True:
        interval = int(os.getenv("CHECK_INTERVAL_SECONDS", 30))
        await asyncio.sleep(interval)

        async with AsyncSessionLocal() as session:
            # Ищем непрочитанные уведомления (is_sent = False)
            stmt = select(Notification).where(Notification.is_sent == False)
            result = await session.execute(stmt)
            pending = result.scalars().all()

            for notif in pending:
                try:
                    await bot.send_message(
                        chat_id=getattr(notif, 'user_telegram_id'),
                        text=f"📢 Новое уведомление с сайта:\n{notif.message_text}"
                    )
                    # Обновляем статус
                    await session.execute(
                        update(Notification)
                        .where(Notification.id == notif.id)
                        .values(is_sent=True)
                    )
                except Exception as e:
                    print(
                        f"Не удалось отправить пользователю {notif.user_telegram_id}: {e}")
            await session.commit()
