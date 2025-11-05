import enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.models.base_model import Base


class User(Base):
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    # Связь один ко многим с Project
    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Связь один ко многим с Task
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class StatusTask(enum.StrEnum):
    IN_PROGRESS = "В работе"
    DELETED = "Удалена"
    SUSPENDED = "Отложена"


class Task(Base):
    title: Mapped[str]
    content: Mapped[str]
    status: Mapped[StatusTask] = mapped_column(default=StatusTask.IN_PROGRESS, server_default=StatusTask.IN_PROGRESS.name)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'))
    result_url: Mapped[str | None] = mapped_column(nullable=True)

    # Связь многие к одному с User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="tasks"
    )

    # Связь многие к одному с Project
    projects: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks"
    )


class Project(Base):
    title: Mapped[str] = mapped_column(unique=True)
    content: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    # Связь многие к одному с User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="projects"
    )

    # Связь один ко многим с Task
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="projects",
        cascade="all, delete-orphan"
    )