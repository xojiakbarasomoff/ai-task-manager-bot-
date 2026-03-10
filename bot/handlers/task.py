from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from db.repositories.user_repo import get_user_by_telegram_id
from db.repositories.project_repo import get_user_projects, get_project_by_id
from db.repositories.task_repo import (
    create_task,
    get_project_tasks,
    get_user_tasks,
    get_task_by_id,
    update_task_status,
    delete_task,
)
from bot.keyboards.task import (
    get_tasks_keyboard,
    get_task_detail_keyboard,
    get_priority_keyboard,
)
from bot.keyboards.project import get_projects_keyboard

router = Router()


class CreateTaskState(StatesGroup):
    waiting_for_project = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_priority = State()
    waiting_for_deadline = State()


# /tasks — vazifalar ro'yxati
@router.message(Command("tasks"))
@router.message(F.text == "✅ Vazifalarim")
async def cmd_tasks(message: Message, db: AsyncSession):
    user = await get_user_by_telegram_id(db, message.from_user.id)
    tasks = await get_user_tasks(db, user.id)

    if not tasks:
        await message.answer(
            "📭 Sizga biriktirilgan vazifalar yo'q.\n"
            "📝 Yangi vazifa yaratish uchun /create_task buyrug'ini yuboring."
        )
        return

    await message.answer(
        f"✅ <b>Sizning vazifalaringiz ({len(tasks)} ta):</b>",
        reply_markup=get_tasks_keyboard(tasks)
    )


# /create_task — yangi vazifa yaratish
@router.message(Command("create_task"))
@router.message(F.text == "📝 Vazifa yaratish")
async def cmd_create_task(message: Message, state: FSMContext, db: AsyncSession):
    user = await get_user_by_telegram_id(db, message.from_user.id)
    projects = await get_user_projects(db, user.id)

    if not projects:
        await message.answer(
            "📭 Avval loyiha yarating!\n"
            "/create_project buyrug'ini yuboring."
        )
        return

    await state.set_state(CreateTaskState.waiting_for_project)
    await message.answer(
        "📁 <b>Qaysi loyiha uchun vazifa yaratmoqchisiz?</b>",
        reply_markup=get_projects_keyboard(projects)
    )


@router.callback_query(
    CreateTaskState.waiting_for_project,
    F.data.startswith("project:")
)
async def process_task_project(callback: CallbackQuery, state: FSMContext):
    project_id = int(callback.data.split(":")[1])
    await state.update_data(project_id=project_id)
    await state.set_state(CreateTaskState.waiting_for_title)
    await callback.message.answer("📝 Vazifa nomini kiriting:")


@router.message(CreateTaskState.waiting_for_title)
async def process_task_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(CreateTaskState.waiting_for_description)
    await message.answer(
        "📄 Vazifa tavsifini kiriting:\n"
        "(O'tkazib yuborish uchun <b>-</b> yuboring)"
    )


@router.message(CreateTaskState.waiting_for_description)
async def process_task_description(message: Message, state: FSMContext):
    description = None if message.text == "-" else message.text
    await state.update_data(description=description)
    await state.set_state(CreateTaskState.waiting_for_priority)
    await message.answer(
        "⚡ Vazifa muhimligini tanlang:",
        reply_markup=get_priority_keyboard()
    )


@router.callback_query(
    CreateTaskState.waiting_for_priority,
    F.data.startswith("priority:")
)
async def process_task_priority(callback: CallbackQuery, state: FSMContext):
    priority = callback.data.split(":")[1]
    await state.update_data(priority=priority)
    await state.set_state(CreateTaskState.waiting_for_deadline)
    await callback.message.answer(
        "📅 Deadline kiriting (format: <b>DD.MM.YYYY</b>):\n"
        "(O'tkazib yuborish uchun <b>-</b> yuboring)"
    )


@router.message(CreateTaskState.waiting_for_deadline)
async def process_task_deadline(
    message: Message, state: FSMContext, db: AsyncSession
):
    deadline = None
    if message.text != "-":
        try:
            deadline = datetime.strptime(message.text, "%d.%m.%Y")
        except ValueError:
            await message.answer(
                "❌ Noto'g'ri format! Qaytadan kiriting (DD.MM.YYYY):"
            )
            return

    data = await state.get_data()
    user = await get_user_by_telegram_id(db, message.from_user.id)

    task = await create_task(
        db=db,
        title=data["title"],
        description=data.get("description"),
        priority=data["priority"],
        deadline=deadline,
        project_id=data["project_id"],
        created_by=user.id,
    )

    await state.clear()

    priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(
        task.priority, "🟡"
    )

    await message.answer(
        f"✅ <b>Vazifa muvaffaqiyatli yaratildi!</b>\n\n"
        f"📝 Nom: <b>{task.title}</b>\n"
        f"⚡ Muhimlik: {priority_icon} {task.priority}\n"
        f"📅 Deadline: {task.deadline.strftime('%d.%m.%Y') if task.deadline else 'Yo\'q'}\n"
        f"🆔 ID: <code>{task.id}</code>"
    )


# Task detail
@router.callback_query(F.data.startswith("task:"))
async def task_detail(callback: CallbackQuery, db: AsyncSession):
    data = callback.data.split(":")[1]

    if data in ["create", "list"]:
        return

    task = await get_task_by_id(db, int(data))
    if not task:
        await callback.answer("Vazifa topilmadi!")
        return

    status_icon = {"TODO": "🔵", "IN_PROGRESS": "🟡", "DONE": "🟢"}.get(
        task.status, "🔵"
    )
    priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(
        task.priority, "🟡"
    )

    await callback.message.edit_text(
        f"📝 <b>{task.title}</b>\n\n"
        f"📄 Tavsif: {task.description or 'Yo\'q'}\n"
        f"🔄 Status: {status_icon} {task.status}\n"
        f"⚡ Muhimlik: {priority_icon} {task.priority}\n"
        f"📅 Deadline: {task.deadline.strftime('%d.%m.%Y') if task.deadline else 'Yo\'q'}",
        reply_markup=get_task_detail_keyboard(task.id)
    )


# Task status o'zgartirish
@router.callback_query(F.data.startswith("task_status:"))
async def task_change_status(callback: CallbackQuery, db: AsyncSession):
    _, task_id, status = callback.data.split(":")
    user = await get_user_by_telegram_id(db, callback.from_user.id)
    task = await update_task_status(db, int(task_id), status, user.id)

    if not task:
        await callback.answer("Vazifa topilmadi!")
        return

    await callback.answer(f"✅ Status: {status}")
    await task_detail(callback, db)


# Task o'chirish
@router.callback_query(F.data.startswith("task_delete:"))
async def task_delete(callback: CallbackQuery, db: AsyncSession):
    task_id = int(callback.data.split(":")[1])
    await delete_task(db, task_id)
    await callback.message.edit_text("✅ Vazifa muvaffaqiyatli o'chirildi!")