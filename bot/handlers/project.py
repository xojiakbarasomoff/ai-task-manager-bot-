from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.user_repo import get_user_by_telegram_id
from db.repositories.project_repo import (
    create_project,
    get_user_projects,
    get_project_by_id,
    delete_project,
)
from bot.keyboards.project import (
    get_projects_keyboard,
    get_project_detail_keyboard,
    get_confirm_delete_keyboard,
)

router = Router()


class CreateProjectState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()


# /projects — loyihalar ro'yxati
@router.message(Command("projects"))
@router.message(F.text == "📁 Loyihalarim")
async def cmd_projects(message: Message, db: AsyncSession):
    user = await get_user_by_telegram_id(db, message.from_user.id)
    projects = await get_user_projects(db, user.id)

    if not projects:
        await message.answer(
            "📭 Sizda hali loyihalar yo'q.\n"
            "➕ Yangi loyiha yaratish uchun /create_project buyrug'ini yuboring."
        )
        return

    await message.answer(
        f"📁 <b>Sizning loyihalaringiz ({len(projects)} ta):</b>",
        reply_markup=get_projects_keyboard(projects)
    )


# /create_project — yangi loyiha yaratish
@router.message(Command("create_project"))
@router.message(F.text == "➕ Loyiha yaratish")
async def cmd_create_project(message: Message, state: FSMContext):
    await state.set_state(CreateProjectState.waiting_for_name)
    await message.answer(
        "📁 <b>Yangi loyiha yaratish</b>\n\n"
        "Loyiha nomini kiriting:"
    )


@router.message(CreateProjectState.waiting_for_name)
async def process_project_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CreateProjectState.waiting_for_description)
    await message.answer(
        "📝 Loyiha tavsifini kiriting:\n"
        "(O'tkazib yuborish uchun <b>-</b> yuboring)"
    )


@router.message(CreateProjectState.waiting_for_description)
async def process_project_description(
    message: Message, state: FSMContext, db: AsyncSession
):
    data = await state.get_data()
    description = None if message.text == "-" else message.text

    user = await get_user_by_telegram_id(db, message.from_user.id)
    project = await create_project(
        db=db,
        name=data["name"],
        description=description,
        owner_id=user.id,
    )

    await state.clear()
    await message.answer(
        f"✅ <b>Loyiha muvaffaqiyatli yaratildi!</b>\n\n"
        f"📁 Nom: <b>{project.name}</b>\n"
        f"📝 Tavsif: {project.description or 'Yo\'q'}\n"
        f"🆔 ID: <code>{project.id}</code>"
    )


# Loyiha detail
@router.callback_query(F.data.startswith("project:"))
async def project_detail(callback: CallbackQuery, db: AsyncSession):
    data = callback.data.split(":")[1]

    if data == "create":
        await callback.message.answer("Loyiha nomini kiriting:")
        return

    if data == "list":
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        projects = await get_user_projects(db, user.id)
        await callback.message.edit_text(
            f"📁 <b>Sizning loyihalaringiz:</b>",
            reply_markup=get_projects_keyboard(projects)
        )
        return

    project = await get_project_by_id(db, int(data))
    if not project:
        await callback.answer("Loyiha topilmadi!")
        return

    await callback.message.edit_text(
        f"📁 <b>{project.name}</b>\n\n"
        f"📝 Tavsif: {project.description or 'Yo\'q'}\n"
        f"📅 Yaratilgan: {project.created_at.strftime('%d.%m.%Y')}",
        reply_markup=get_project_detail_keyboard(project.id)
    )


# Loyiha o'chirish
@router.callback_query(F.data.startswith("project_delete:"))
async def project_delete_confirm(callback: CallbackQuery):
    project_id = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "🗑 <b>Loyihani o'chirishni tasdiqlaysizmi?</b>\n"
        "Bu amalni ortga qaytarib bo'lmaydi!",
        reply_markup=get_confirm_delete_keyboard(project_id)
    )


@router.callback_query(F.data.startswith("project_delete_confirm:"))
async def project_delete(callback: CallbackQuery, db: AsyncSession):
    project_id = int(callback.data.split(":")[1])
    await delete_project(db, project_id)
    await callback.message.edit_text(
        "✅ Loyiha muvaffaqiyatli o'chirildi!"
    )