
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import get_weekly_summary, get_daily_summary, get_users_for_notifications

scheduler = AsyncIOScheduler() # создаем сам планировщик, он будет отвечать за выполнение заданий по расписанию


def schedule_jobs(bot): # функция настраивает задачи для планировщика
    from aiogram import Bot  # импорт тут, чтобы избежать циклических импортов

    async def send_daily_notifications():
        users = get_users_for_notifications() # получаем всех пользователей, у которых включены уведомления
        for user_id in users: # для каждого пользователя формируем сводку
            daily = get_daily_summary(user_id)
            weekly = get_weekly_summary(user_id)

            lines = ["📅 *Summary for the day*\n"]
            if daily:
                for category, total in daily:
                    lines.append(f"• {category}: {total}₸")
            else:
                lines.append("There are no records for today.")

            lines.append("\n🗓 *Summary for the week*\n")
            if weekly:
                for category, total in weekly:
                    lines.append(f"• {category}: {total}₸")
            else:
                lines.append("There are no records for the week.")

            await bot.send_message(chat_id=user_id, text="\n".join(lines), parse_mode="Markdown")

    scheduler.add_job(send_daily_notifications, "cron", hour=21, minute=53)
    # добавляем задачу в планировщик: каждый день в 21:53 будет выполняться функция send_daily_notifications