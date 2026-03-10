import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import settings
from core.logger import setup_logger
from db.database import create_tables
from bot.middlewares.db import DbSessionMiddleware
from bot.handlers.start import router as start_router
from bot.handlers.project import router as project_router
from bot.handlers.task import router as task_router
from bot.handlers.assign import router as assign_router
from bot.handlers.ai_tasks import router as ai_tasks_router
from bot.handlers.stats import router as stats_router
from bot.handlers.notifications import router as notifications_router

logger = setup_logger()


async def main():
    logger.info("🚀 AI Task Manager Bot ishga tushmoqda...")

    # DB jadvallarini yaratish
    await create_tables()
    logger.info("✅ Database tayyor")

    # Bot va Dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = RedisStorage.from_url(settings.REDIS_URL)
    dp = Dispatcher(storage=storage)

    # Middleware ulash
    dp.update.middleware(DbSessionMiddleware())

    # Routerlarni ulash
    dp.include_router(start_router)
    dp.include_router(notifications_router)
    dp.include_router(project_router)
    dp.include_router(task_router)
    dp.include_router(assign_router)
    dp.include_router(ai_tasks_router)
    dp.include_router(stats_router)

    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
    finally:
        await bot.session.close()
        logger.info("🛑 Bot to'xtatildi")


if __name__ == "__main__":
    asyncio.run(main())