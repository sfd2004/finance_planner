
import asyncio # библиотека для асинхроности
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from db import init_db
from handlers import router
from scheduler import scheduler, schedule_jobs  # импортируем планировщик

init_db() # запускает базу данных

async def main():
    bot = Bot(token=BOT_TOKEN) #создаем экхемпляр бота
    dp = Dispatcher() #диспетчер обрабатывает все взодящие сообщения

    dp.include_router(router)

    schedule_jobs(bot)         # добавляем запланированые задачи 
    scheduler.start()          # запускаем планировщик

    await dp.start_polling(bot) #запуск бота

if __name__ == "__main__":
    asyncio.run(main())
