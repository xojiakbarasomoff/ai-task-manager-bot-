from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from db.database import Base


class ProjectMember(Base):
    __tablename__ = "project_members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(50), default="member", nullable=False
    )  # "admin" yoki "member"
    joined_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", backref="project_members")

    def __repr__(self):
        return f"<ProjectMember user={self.user_id} project={self.project_id} role={self.role}>"