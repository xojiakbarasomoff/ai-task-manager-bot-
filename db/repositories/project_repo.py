from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.project import Project
from db.models.project_member import ProjectMember


async def create_project(
    db: AsyncSession,
    name: str,
    description: str | None,
    owner_id: int,
) -> Project:
    project = Project(
        name=name,
        description=description,
        owner_id=owner_id,
    )
    db.add(project)
    await db.flush()

    # Owner'ni member sifatida ham qo'shamiz
    member = ProjectMember(
        project_id=project.id,
        user_id=owner_id,
        role="admin",
    )
    db.add(member)
    await db.commit()
    await db.refresh(project)
    return project


async def get_user_projects(
    db: AsyncSession, user_id: int
) -> list[Project]:
    result = await db.execute(
        select(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == user_id)
        .order_by(Project.created_at.desc())
    )
    return result.scalars().all()


async def get_project_by_id(
    db: AsyncSession, project_id: int
) -> Project | None:
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    return result.scalar_one_or_none()


async def delete_project(
    db: AsyncSession, project_id: int
) -> bool:
    project = await get_project_by_id(db, project_id)
    if not project:
        return False
    await db.delete(project)
    await db.commit()
    return True