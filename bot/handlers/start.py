from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.user_repo import get_or_create_user
from bot.keyboards.main_menu import get_main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, db: AsyncSession):
    user, is_created = await get_or_create_user(
        db=db,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )

    if is_created:
        text = (
            f"👋 Salom, <b>{message.from_user.full_name}</b>!\n\n"
            f"🤖 <b>AI Task Manager Bot</b>ga xush kelibsiz!\n\n"
            f"Bu bot orqali:\n"
            f"📁 Loyihalar yaratishingiz\n"
            f"✅ Vazifalar boshqarishingiz\n"
            f"👥 Jamoa bilan ishlashingiz\n"
            f"🤖 AI yordamida vazifalar generatsiya qilishingiz mumkin!\n\n"
            f"Boshlash uchun quyidagi menyudan foydalaning 👇"
        )
    else:
        text = (
            f"👋 Qaytib keldingiz, <b>{message.from_user.full_name}</b>!\n\n"
            f"Menyudan amalni tanlang 👇"
        )

    await message.answer(text, reply_markup=get_main_menu())