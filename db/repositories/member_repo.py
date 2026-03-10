from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.project_member import ProjectMember
from db.models.user import User


async def get_project_members(
    db: AsyncSession, project_id: int
) -> list[User]:
    result = await db.execute(
        select(User)
        .join(ProjectMember, ProjectMember.user_id == User.id)
        .where(ProjectMember.project_id == project_id)
    )
    return result.scalars().all()


async def add_member_to_project(
    db: AsyncSession,
    project_id: int,
    user_id: int,
    role: str = "member",
) -> ProjectMember:
    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def is_project_member(
    db: AsyncSession,
    project_id: int,
    user_id: int,
) -> bool:
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def remove_member(
    db: AsyncSession,
    project_id: int,
    user_id: int,
) -> bool:
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        return False
    await db.delete(member)
    await db.commit()
    return True