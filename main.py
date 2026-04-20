import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from database import engine
from handlers import router
from notifier import check_and_send_notifications

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():
    if BOT_TOKEN is None:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем роутер с обработчиками
    dp.include_router(router)

    # Запускаем фоновую задачу проверки уведомлений
    asyncio.create_task(check_and_send_notifications(bot))

    # Стартуем Long Polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
