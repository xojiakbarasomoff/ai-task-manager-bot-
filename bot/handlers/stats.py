from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.user_repo import get_user_by_telegram_id
from db.repositories.project_repo import get_user_projects, get_project_by_id
from db.repositories.stats_repo import get_user_stats, get_project_stats

router = Router()


def get_stats_keyboard(projects) -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(
            text="👤 Mening statistikam",
            callback_data="stats:personal"
        )
    ]]
    for project in projects:
        buttons.append([
            InlineKeyboardButton(
                text=f"📁 {project.name}",
                callback_data=f"stats:project:{project.id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def format_progress_bar(percent: int) -> str:
    filled = int(percent / 10)
    empty = 10 - filled
    return "█" * filled + "░" * empty


# /stats
@router.message(Command("stats"))
@router.message(F.text == "📊 Statistika")
async def cmd_stats(message: Message, db: AsyncSession):
    user = await get_user_by_telegram_id(db, message.from_user.id)
    projects = await get_user_projects(db, user.id)

    await message.answer(
        "📊 <b>Statistika</b>\n\n"
        "Qaysi statistikani ko'rmoqchisiz?",
        reply_markup=get_stats_keyboard(projects)
    )


# Shaxsiy statistika
@router.callback_query(F.data == "stats:personal")
async def personal_stats(callback: CallbackQuery, db: AsyncSession):
    user = await get_user_by_telegram_id(db, callback.from_user.id)
    stats = await get_user_stats(db, user.id)

    progress_bar = format_progress_bar(stats["productivity"])

    await callback.message.edit_text(
        f"👤 <b>Sizning statistikangiz</b>\n\n"
        f"📁 Loyihalar: <b>{stats['projects']}</b>\n\n"
        f"📊 Vazifalar:\n"
        f"  🔵 TODO: <b>{stats['todo']}</b>\n"
        f"  🟡 Jarayonda: <b>{stats['in_progress']}</b>\n"
        f"  🟢 Bajarildi: <b>{stats['done']}</b>\n"
        f"  🔴 Muddati o'tgan: <b>{stats['overdue']}</b>\n"
        f"  📋 Jami: <b>{stats['total']}</b>\n\n"
        f"⚡ Samaradorlik:\n"
        f"  {progress_bar} <b>{stats['productivity']}%</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="stats:back"
            )
        ]])
    )


# Loyiha statistikasi
@router.callback_query(F.data.startswith("stats:project:"))
async def project_stats(callback: CallbackQuery, db: AsyncSession):
    project_id = int(callback.data.split(":")[2])
    project = await get_project_by_id(db, project_id)
    stats = await get_project_stats(db, project_id)

    progress_bar = format_progress_bar(stats["progress"])

    await callback.message.edit_text(
        f"📁 <b>{project.name}</b> statistikasi\n\n"
        f"📊 Vazifalar:\n"
        f"  🟡 Jarayonda: <b>{stats['in_progress']}</b>\n"
        f"  🟢 Bajarildi: <b>{stats['done']}</b>\n"
        f"  🔴 Muddati o'tgan: <b>{stats['overdue']}</b>\n"
        f"  📋 Jami: <b>{stats['total']}</b>\n\n"
        f"📈 Progress:\n"
        f"  {progress_bar} <b>{stats['progress']}%</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="stats:back"
            )
        ]])
    )


# Orqaga
@router.callback_query(F.data == "stats:back")
async def stats_back(callback: CallbackQuery, db: AsyncSession):
    user = await get_user_by_telegram_id(db, callback.from_user.id)
    projects = await get_user_projects(db, user.id)

    await callback.message.edit_text(
        "📊 <b>Statistika</b>\n\n"
        "Qaysi statistikani ko'rmoqchisiz?",
        reply_markup=get_stats_keyboard(projects)
    )