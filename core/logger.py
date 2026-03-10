import sys
from loguru import logger
from core.config import settings


def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
               "<level>{message}</level>",
        colorize=True,
    )
    logger.add(
        "logs/bot.log",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    return logger