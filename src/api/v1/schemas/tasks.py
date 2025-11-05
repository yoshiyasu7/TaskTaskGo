from enum import Enum
from pydantic import BaseModel, ConfigDict


class StatusTask(str, Enum):
    IN_PROGRESS = "В работе"
    DELETED = "Удалена"
    SUSPENDED = "Отложена"
    DONE = "Выполнена"


class TaskPydantic(BaseModel):
    title: str
    content: str | None = None
    status: StatusTask | None = StatusTask.IN_PROGRESS
    project_id: int
    user_id: int | None = None
    result_url: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "title": "Task title",
                "content": "Task content",
                "status": "Task status"
            }
        }
    )


class TaskResultURL(BaseModel):
    status: StatusTask | None = StatusTask.DONE
    result_url: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    status: StatusTask | None = None


class TaskUpdateWithUser(BaseModel):
    title: str | None = None
    content: str | None = None
    status: StatusTask | None = None
    user_id: int


class TaskRead(BaseModel):
    id: int
    title: str | None = None
    content: str | None = None
    status: StatusTask | None = None
    project_id: int
    user_id: int | None = None
    result_url: str | None = None