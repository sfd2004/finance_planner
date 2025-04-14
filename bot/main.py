
import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from db import init_db
from handlers import router
from scheduler import scheduler, schedule_jobs  # импортируем планировщик

init_db()

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)

    schedule_jobs(bot)         # запускаем задания
    scheduler.start()          # стартуем планировщик

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
