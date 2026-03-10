from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from db.models.task import Task
from db.models.project import Project
from db.models.project_member import ProjectMember


async def get_user_stats(db: AsyncSession, user_id: int) -> dict:
    """Foydalanuvchi statistikasini qaytaradi"""

    # Jami vazifalar
    total_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.assigned_to == user_id
        )
    )
    total = total_result.scalar() or 0

    # Bajarilgan vazifalar
    done_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.assigned_to == user_id,
            Task.status == "DONE"
        )
    )
    done = done_result.scalar() or 0

    # Jarayondagi vazifalar
    in_progress_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.assigned_to == user_id,
            Task.status == "IN_PROGRESS"
        )
    )
    in_progress = in_progress_result.scalar() or 0

    # Muddati o'tgan vazifalar
    overdue_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.assigned_to == user_id,
            Task.status != "DONE",
            Task.deadline < datetime.utcnow(),
            Task.deadline.isnot(None),
        )
    )
    overdue = overdue_result.scalar() or 0

    # Todo vazifalar
    todo_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.assigned_to == user_id,
            Task.status == "TODO"
        )
    )
    todo = todo_result.scalar() or 0

    # Loyihalar soni
    projects_result = await db.execute(
        select(func.count(ProjectMember.id)).where(
            ProjectMember.user_id == user_id
        )
    )
    projects = projects_result.scalar() or 0

    # Productivity score hisoblash
    if total > 0:
        productivity = int((done / total) * 100)
    else:
        productivity = 0

    return {
        "total": total,
        "done": done,
        "in_progress": in_progress,
        "todo": todo,
        "overdue": overdue,
        "projects": projects,
        "productivity": productivity,
    }


async def get_project_stats(
    db: AsyncSession, project_id: int
) -> dict:
    """Loyiha statistikasini qaytaradi"""

    total_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id
        )
    )
    total = total_result.scalar() or 0

    done_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.status == "DONE"
        )
    )
    done = done_result.scalar() or 0

    in_progress_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.status == "IN_PROGRESS"
        )
    )
    in_progress = in_progress_result.scalar() or 0

    overdue_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.status != "DONE",
            Task.deadline < datetime.utcnow(),
            Task.deadline.isnot(None),
        )
    )
    overdue = overdue_result.scalar() or 0

    progress = int((done / total) * 100) if total > 0 else 0

    return {
        "total": total,
        "done": done,
        "in_progress": in_progress,
        "overdue": overdue,
        "progress": progress,
    }