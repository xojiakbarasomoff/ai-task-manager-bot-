from aiogram import Bot
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.project_member import ProjectMember
from db.models.user import User
from db.models.task import Task
from db.models.project import Project


async def notify_project_members(
    bot: Bot,
    db: AsyncSession,
    project_id: int,
    message: str,
    exclude_user_id: int | None = None,
):
    """Loyiha barcha a'zolariga xabar yuboradi"""
    result = await db.execute(
        select(User)
        .join(ProjectMember, ProjectMember.user_id == User.id)
        .where(ProjectMember.project_id == project_id)
    )
    members = result.scalars().all()

    for member in members:
        if exclude_user_id and member.id == exclude_user_id:
            continue
        try:
            await bot.send_message(
                chat_id=member.telegram_id,
                text=message,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            print(f"Xabar yuborishda xato {member.telegram_id}: {e}")


async def notify_task_assigned(
    bot: Bot,
    db: AsyncSession,
    task: Task,
    assigned_by_name: str,
):
    """Vazifa biriktirilganda assignee ga xabar yuboradi"""
    if not task.assigned_to:
        return

    result = await db.execute(
        select(User).where(User.id == task.assigned_to)
    )
    user = result.scalar_one_or_none()
    if not user:
        return

    priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(
        task.priority, "🟡"
    )

    try:
        await bot.send_message(
            chat_id=user.telegram_id,
            text=(
                f"📬 <b>Sizga yangi vazifa biriktirildi!</b>\n\n"
                f"📝 Vazifa: <b>{task.title}</b>\n"
                f"⚡ Muhimlik: {priority_icon} {task.priority}\n"
                f"📅 Deadline: "
                f"{task.deadline.strftime('%d.%m.%Y') if task.deadline else 'Yo\'q'}\n"
                f"👤 Biriktirgan: <b>{assigned_by_name}</b>"
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        print(f"Xabar yuborishda xato: {e}")


async def notify_task_status_changed(
    bot: Bot,
    db: AsyncSession,
    task: Task,
    old_status: str,
    changed_by_name: str,
    project_id: int,
):
    """Task status o'zgarganda loyiha a'zolariga xabar yuboradi"""
    status_icon = {"TODO": "🔵", "IN_PROGRESS": "🟡", "DONE": "🟢"}.get(
        task.status, "🔵"
    )

    message = (
        f"🔄 <b>Vazifa statusi o'zgartirildi!</b>\n\n"
        f"📝 Vazifa: <b>{task.title}</b>\n"
        f"📊 Status: {old_status} → {status_icon} <b>{task.status}</b>\n"
        f"👤 O'zgartirgan: <b>{changed_by_name}</b>"
    )

    await notify_project_members(bot, db, project_id, message)


async def notify_task_completed(
    bot: Bot,
    db: AsyncSession,
    task: Task,
    completed_by_name: str,
    project_id: int,
):
    """Vazifa bajarilganda loyiha a'zolariga xabar yuboradi"""
    message = (
        f"✅ <b>Vazifa bajarildi!</b>\n\n"
        f"📝 Vazifa: <b>{task.title}</b>\n"
        f"👤 Bajardi: <b>{completed_by_name}</b>\n\n"
        f"🎉 Tabriklaymiz!"
    )

    await notify_project_members(bot, db, project_id, message)