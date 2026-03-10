from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.user_repo import get_user_by_telegram_id
from db.repositories.task_repo import get_task_by_id, update_task_status
from utils.notifier import (
    notify_task_status_changed,
    notify_task_completed,
    notify_task_assigned,
)

router = Router()


@router.callback_query(F.data.startswith("task_status:"))
async def task_status_with_notification(
    callback: CallbackQuery, db: AsyncSession, bot: Bot
):
    _, task_id, new_status = callback.data.split(":")
    task = await get_task_by_id(db, int(task_id))

    if not task:
        await callback.answer("Vazifa topilmadi!")
        return

    old_status = task.status
    user = await get_user_by_telegram_id(db, callback.from_user.id)
    user_name = user.full_name or user.username or "Noma'lum"

    # Statusni yangilash
    updated_task = await update_task_status(
        db, int(task_id), new_status, user.id
    )

    await callback.answer(f"✅ Status: {new_status}")

    # Bildirishnoma yuborish
    if new_status == "DONE":
        await notify_task_completed(
            bot=bot,
            db=db,
            task=updated_task,
            completed_by_name=user_name,
            project_id=updated_task.project_id,
        )
    else:
        await notify_task_status_changed(
            bot=bot,
            db=db,
            task=updated_task,
            old_status=old_status,
            changed_by_name=user_name,
            project_id=updated_task.project_id,
        )

    # Task detail ni yangilash
    from bot.keyboards.task import get_task_detail_keyboard
    from aiogram.enums import ParseMode

    status_icon = {"TODO": "🔵", "IN_PROGRESS": "🟡", "DONE": "🟢"}.get(
        updated_task.status, "🔵"
    )
    priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(
        updated_task.priority, "🟡"
    )

    await callback.message.edit_text(
        f"📝 <b>{updated_task.title}</b>\n\n"
        f"📄 Tavsif: {updated_task.description or 'Yo\'q'}\n"
        f"🔄 Status: {status_icon} {updated_task.status}\n"
        f"⚡ Muhimlik: {priority_icon} {updated_task.priority}\n"
        f"📅 Deadline: "
        f"{updated_task.deadline.strftime('%d.%m.%Y') if updated_task.deadline else 'Yo\'q'}",
        reply_markup=get_task_detail_keyboard(updated_task.id)
    )