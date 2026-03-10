from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.user import User


async def get_user_by_telegram_id(
    db: AsyncSession, telegram_id: int
) -> User | None:
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    telegram_id: int,
    username: str | None,
    full_name: str | None,
) -> User:
    user = User(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_user(
    db: AsyncSession,
    telegram_id: int,
    username: str | None,
    full_name: str | None,
) -> tuple[User, bool]:
    """
    User mavjud bo'lsa qaytaradi,
    bo'lmasa yangi yaratadi.
    Returns: (user, is_created)
    """
    user = await get_user_by_telegram_id(db, telegram_id)
    if user:
        return user, False

    user = await create_user(db, telegram_id, username, full_name)
    return user, True