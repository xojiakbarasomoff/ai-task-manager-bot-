from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from db.models.task import Task
from db.models.task_log import TaskLog


async def create_task(
    db: AsyncSession,
    title: str,
    description: str | None,
    priority: str,
    deadline: datetime | None,
    project_id: int,
    created_by: int,
    assigned_to: int | None = None,
) -> Task:
    task = Task(
        title=title,
        description=description,
        priority=priority,
        deadline=deadline,
        project_id=project_id,
        created_by=created_by,
        assigned_to=assigned_to,
        status="TODO",
    )
    db.add(task)
    await db.flush()

    # Log yozish
    log = TaskLog(
        task_id=task.id,
        user_id=created_by,
        action="Task yaratildi",
    )
    db.add(log)
    await db.commit()
    await db.refresh(task)
    return task


async def get_project_tasks(
    db: AsyncSession, project_id: int
) -> list[Task]:
    result = await db.execute(
        select(Task)
        .where(Task.project_id == project_id)
        .order_by(Task.created_at.desc())
    )
    return result.scalars().all()


async def get_user_tasks(
    db: AsyncSession, user_id: int
) -> list[Task]:
    result = await db.execute(
        select(Task)
        .where(Task.assigned_to == user_id)
        .order_by(Task.created_at.desc())
    )
    return result.scalars().all()


async def get_task_by_id(
    db: AsyncSession, task_id: int
) -> Task | None:
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    return result.scalar_one_or_none()


async def update_task_status(
    db: AsyncSession,
    task_id: int,
    status: str,
    user_id: int,
) -> Task | None:
    task = await get_task_by_id(db, task_id)
    if not task:
        return None

    old_status = task.status
    task.status = status

    log = TaskLog(
        task_id=task.id,
        user_id=user_id,
        action=f"Status o'zgartirildi: {old_status} → {status}",
    )
    db.add(log)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(
    db: AsyncSession, task_id: int
) -> bool:
    task = await get_task_by_id(db, task_id)
    if not task:
        return False
    await db.delete(task)
    await db.commit()
    return True