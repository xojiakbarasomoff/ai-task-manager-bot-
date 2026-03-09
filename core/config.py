from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: str

    # Database
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "ai_task_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # AI
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    AI_PROVIDER: Literal["openai", "anthropic"] = "anthropic"

    # App
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    REMINDER_CHECK_INTERVAL: int = 300

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()