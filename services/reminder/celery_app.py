from celery import Celery
from celery.schedules import crontab
from core.config import settings


celery_app = Celery(
    "ai_task_bot",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["services.reminder.tasks"],
)

celery_app.conf.update(
    timezone="Asia/Tashkent",
    enable_utc=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

# Har 5 daqiqada deadline tekshirish
celery_app.conf.beat_schedule = {
    "check-deadlines": {
        "task": "services.reminder.tasks.check_deadlines",
        "schedule": crontab(minute="*/5"),
    },
}