import asyncio
from datetime import datetime, timedelta
from celery import shared_task
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.database import AsyncSessionLocal
from db.models.task import Task
from db.models.user import User


async def send_reminder(bot: Bot, telegram_id: int, task: Task):
    now = datetime.utcnow()
    diff = task.deadline - now
    hours = int(diff.total_seconds() // 3600)
    minutes = int((diff.total_seconds() % 3600) // 60)

    if hours > 0:
        time_left = f"{hours} soat"
    else:
        time_left = f"{minutes} daqiqa"

    priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(
        task.priority, "🟡"
    )

    await bot.send_message(
        chat_id=telegram_id,
        text=(
            f"⏰ <b>Deadline eslatmasi!</b>\n\n"
            f"📝 Vazifa: <b>{task.title}</b>\n"
            f"⚡ Muhimlik: {priority_icon} {task.priority}\n"
            f"⏳ Qolgan vaqt: <b>{time_left}</b>\n"
            f"📅 Deadline: {task.deadline.strftime('%d.%m.%Y %H:%M')}"
        ),
        parse_mode=ParseMode.HTML,
    )


async def check_deadlines_async():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()
        soon = now + timedelta(hours=2)

        # Deadline 2 soat ichida bo'lgan vazifalarni topish
        result = await db.execute(
            select(Task).where(
                Task.deadline >= now,
                Task.deadline <= soon,
                Task.status != "DONE",
                Task.assigned_to.isnot(None),
            )
        )
        tasks = result.scalars().all()

        for task in tasks:
            # Assigned user telegram_id sini olish
            user_result = await db.execute(
                select(User).where(User.id == task.assigned_to)
            )
            user = user_result.scalar_one_or_none()

            if user:
                try:
                    await send_reminder(bot, user.telegram_id, task)
                except Exception as e:
                    print(f"Reminder yuborishda xato: {e}")

    await bot.session.close()


@shared_task(name="services.reminder.tasks.check_deadlines")
def check_deadlines():
    """Celery task — har 5 daqiqada ishga tushadi"""
    asyncio.run(check_deadlines_async())