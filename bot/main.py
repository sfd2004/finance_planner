import asyncio # модуль для выполнения асинхронных задач 
from aiogram import Bot, Dispatcher #бот - прямой канал связи с ботом, диспетчер - маршрутизатор 
from config import BOT_TOKEN
from db import init_db
from handlers import router

init_db() #запуск функйии init.db что бы база данных была готова к исп.

async def main(): #определяет функцию
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher() #создает распределитель всех входяхиъ сообщений
    dp.include_router(router) #подключает все маршруты из handlers
    await dp.start_polling(bot) #запуск бота и бесконечный цикл проверки входящих сообшений

if __name__ == "__main__":
    asyncio.run(main()) #запуск функции 
