from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.user_repo import get_user_by_telegram_id
from db.repositories.project_repo import get_user_projects, get_project_by_id
from db.repositories.task_repo import create_task
from services.ai.generator import generate_tasks
from bot.keyboards.project import get_projects_keyboard

router = Router()


class AITaskState(StatesGroup):
    waiting_for_idea = State()
    waiting_for_project = State()
    waiting_for_confirm = State()


def get_confirm_keyboard(project_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Loyihaga qo'shish",
                    callback_data=f"ai_confirm:{project_id}"
                ),
                InlineKeyboardButton(
                    text="🔄 Qayta generatsiya",
                    callback_data="ai_regenerate"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data="ai_cancel"
                ),
            ]
        ]
    )


# /ai_tasks
@router.message(Command("ai_tasks"))
@router.message(F.text == "🤖 AI Vazifalar")
async def cmd_ai_tasks(message: Message, state: FSMContext):
    await state.set_state(AITaskState.waiting_for_idea)
    await message.answer(
        "🤖 <b>AI Vazifa Generatori</b>\n\n"
        "Loyiha g'oyangizni kiriting va men avtomatik "
        "vazifalar ro'yxatini tayyorlayman!\n\n"
        "Masalan:\n"
        "• E-commerce veb-sayt yaratish\n"
        "• Mobil ilova ishlab chiqish\n"
        "• Blog platformasi qurish"
    )


@router.message(AITaskState.waiting_for_idea)
async def process_ai_idea(
    message: Message, state: FSMContext, db: AsyncSession
):
    idea = message.text
    await state.update_data(idea=idea)

    # Loading xabari
    loading_msg = await message.answer(
        "⏳ <b>AI vazifalarni generatsiya qilmoqda...</b>"
    )

    try:
        tasks = await generate_tasks(idea)
        await state.update_data(tasks=tasks)

        # Vazifalar ro'yxatini chiroyli ko'rsatish
        tasks_text = "\n".join(
            f"  {i+1}. {task}" for i, task in enumerate(tasks)
        )

        await loading_msg.delete()
        await message.answer(
            f"🤖 <b>AI taklif qilgan vazifalar:</b>\n\n"
            f"{tasks_text}\n\n"
            f"Bu vazifalarni qaysi loyihaga qo'shmoqchisiz?"
        )

        # Loyihalar ro'yxatini ko'rsatish
        user = await get_user_by_telegram_id(db, message.from_user.id)
        projects = await get_user_projects(db, user.id)

        if not projects:
            await message.answer(
                "📭 Avval loyiha yarating!\n"
                "/create_project buyrug'ini yuboring."
            )
            await state.clear()
            return

        await state.set_state(AITaskState.waiting_for_project)
        await message.answer(
            "📁 <b>Loyihani tanlang:</b>",
            reply_markup=get_projects_keyboard(projects)
        )

    except Exception as e:
        await loading_msg.delete()
        await message.answer(
            "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.\n"
            f"Xato: {str(e)}"
        )
        await state.clear()


@router.callback_query(
    AITaskState.waiting_for_project,
    F.data.startswith("project:")
)
async def process_ai_project(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession
):
    project_id = int(callback.data.split(":")[1])
    project = await get_project_by_id(db, project_id)
    await state.update_data(project_id=project_id)

    data = await state.get_data()
    tasks = data.get("tasks", [])
    tasks_text = "\n".join(
        f"  {i+1}. {task}" for i, task in enumerate(tasks)
    )

    await state.set_state(AITaskState.waiting_for_confirm)
    await callback.message.answer(
        f"📁 Loyiha: <b>{project.name}</b>\n\n"
        f"🤖 Quyidagi vazifalar qo'shiladi:\n\n"
        f"{tasks_text}",
        reply_markup=get_confirm_keyboard(project_id)
    )


@router.callback_query(
    AITaskState.waiting_for_confirm,
    F.data.startswith("ai_confirm:")
)
async def process_ai_confirm(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession
):
    project_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    tasks = data.get("tasks", [])

    user = await get_user_by_telegram_id(db, callback.from_user.id)

    # Barcha vazifalarni DB ga saqlash
    for title in tasks:
        await create_task(
            db=db,
            title=title,
            description=None,
            priority="MEDIUM",
            deadline=None,
            project_id=project_id,
            created_by=user.id,
        )

    await state.clear()
    await callback.message.answer(
        f"✅ <b>{len(tasks)} ta vazifa muvaffaqiyatli qo'shildi!</b>\n\n"
        f"Vazifalarni ko'rish uchun /tasks buyrug'ini yuboring."
    )


@router.callback_query(F.data == "ai_regenerate")
async def process_ai_regenerate(
    callback: CallbackQuery, state: FSMContext
):
    await state.set_state(AITaskState.waiting_for_idea)
    await callback.message.answer(
        "🔄 Yangi g'oyangizni kiriting:"
    )


@router.callback_query(F.data == "ai_cancel")
async def process_ai_cancel(
    callback: CallbackQuery, state: FSMContext
):
    await state.clear()
    await callback.message.answer(
        "❌ Bekor qilindi."
    )