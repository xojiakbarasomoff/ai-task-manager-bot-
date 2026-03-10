from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.user_repo import get_user_by_telegram_id
from db.repositories.project_repo import get_user_projects
from db.repositories.task_repo import get_project_tasks, get_task_by_id
from db.repositories.member_repo import get_project_members
from db.models.task_log import TaskLog
from bot.keyboards.project import get_projects_keyboard

router = Router()


class AssignTaskState(StatesGroup):
    waiting_for_project = State()
    waiting_for_task = State()
    waiting_for_user = State()


def get_tasks_for_assign(tasks) -> InlineKeyboardMarkup:
    buttons = []
    for task in tasks:
        if task.status != "DONE":
            buttons.append([
                InlineKeyboardButton(
                    text=f"📝 {task.title}",
                    callback_data=f"assign_task:{task.id}"
                )
            ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_members_keyboard(members, task_id) -> InlineKeyboardMarkup:
    buttons = []
    for member in members:
        name = member.full_name or member.username or str(member.telegram_id)
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {name}",
                callback_data=f"assign_user:{task_id}:{member.id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# /assign_task
@router.message(Command("assign_task"))
async def cmd_assign_task(
    message: Message, state: FSMContext, db: AsyncSession
):
    user = await get_user_by_telegram_id(db, message.from_user.id)
    projects = await get_user_projects(db, user.id)

    if not projects:
        await message.answer(
            "📭 Avval loyiha yarating!\n"
            "/create_project buyrug'ini yuboring."
        )
        return

    await state.set_state(AssignTaskState.waiting_for_project)
    await message.answer(
        "📁 <b>Qaysi loyihadagi vazifani belgilmoqchisiz?</b>",
        reply_markup=get_projects_keyboard(projects)
    )


@router.callback_query(
    AssignTaskState.waiting_for_project,
    F.data.startswith("project:")
)
async def process_assign_project(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession
):
    project_id = int(callback.data.split(":")[1])
    await state.update_data(project_id=project_id)

    tasks = await get_project_tasks(db, project_id)
    active_tasks = [t for t in tasks if t.status != "DONE"]

    if not active_tasks:
        await callback.message.answer(
            "📭 Bu loyihada aktiv vazifalar yo'q!"
        )
        await state.clear()
        return

    await state.set_state(AssignTaskState.waiting_for_task)
    await callback.message.answer(
        "📝 <b>Qaysi vazifani belgilmoqchisiz?</b>",
        reply_markup=get_tasks_for_assign(active_tasks)
    )


@router.callback_query(
    AssignTaskState.waiting_for_task,
    F.data.startswith("assign_task:")
)
async def process_assign_task(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession
):
    task_id = int(callback.data.split(":")[1])
    await state.update_data(task_id=task_id)

    data = await state.get_data()
    members = await get_project_members(db, data["project_id"])

    if not members:
        await callback.message.answer(
            "📭 Bu loyihada a'zolar yo'q!"
        )
        await state.clear()
        return

    await state.set_state(AssignTaskState.waiting_for_user)
    await callback.message.answer(
        "👤 <b>Kimga belgilmoqchisiz?</b>",
        reply_markup=get_members_keyboard(members, task_id)
    )


@router.callback_query(
    AssignTaskState.waiting_for_user,
    F.data.startswith("assign_user:")
)
async def process_assign_user(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession
):
    _, task_id, user_id = callback.data.split(":")
    task = await get_task_by_id(db, int(task_id))

    if not task:
        await callback.answer("Vazifa topilmadi!")
        await state.clear()
        return

    task.assigned_to = int(user_id)

    # Log yozish
    assigner = await get_user_by_telegram_id(db, callback.from_user.id)
    log = TaskLog(
        task_id=task.id,
        user_id=assigner.id,
        action=f"Vazifa user_id={user_id} ga biriktirildi",
    )
    db.add(log)
    await db.commit()

    await state.clear()
    await callback.message.answer(
        f"✅ <b>Vazifa muvaffaqiyatli biriktirildi!</b>\n\n"
        f"📝 Vazifa: <b>{task.title}</b>"
    )