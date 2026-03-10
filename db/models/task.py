from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="TODO", nullable=False
    )  # TODO, IN_PROGRESS, DONE
    priority: Mapped[str] = mapped_column(
        String(50), default="MEDIUM", nullable=False
    )  # LOW, MEDIUM, HIGH
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    assignee: Mapped["User"] = relationship("User", foreign_keys=[assigned_to])
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    logs: Mapped[list["TaskLog"]] = relationship(
        "TaskLog", backref="task", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Task {self.id} - {self.title} [{self.status}]>"