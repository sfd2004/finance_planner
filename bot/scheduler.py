
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import get_weekly_summary, get_daily_summary, get_users_for_notifications
scheduler = AsyncIOScheduler()


def schedule_jobs(bot):
    from aiogram import Bot  # импорт тут, чтобы избежать циклических импортов

    async def send_daily_notifications():
        users = get_users_for_notifications()
        for user_id in users:
            daily = get_daily_summary(user_id)
            weekly = get_weekly_summary(user_id)

            lines = ["📅 *Сводка за день*\n"]
            if daily:
                for category, total in daily:
                    lines.append(f"• {category}: {total}₸")
            else:
                lines.append("Нет записей за сегодня.")

            lines.append("\n🗓 *Сводка за неделю*\n")
            if weekly:
                for category, total in weekly:
                    lines.append(f"• {category}: {total}₸")
            else:
                lines.append("Нет записей за неделю.")

            await bot.send_message(chat_id=user_id, text="\n".join(lines), parse_mode="Markdown")

    scheduler.add_job(send_daily_notifications, "cron", hour=21, minute=53)
