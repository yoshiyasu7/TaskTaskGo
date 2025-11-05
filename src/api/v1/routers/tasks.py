from typing import List

from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.logger import app_logger, error_logger
from src.infrastructure.database.session import get_session_with_commit
from src.api.core.security import get_current_user, JWTBearer
from src.api.v1.schemas.tasks import TaskPydantic, TaskUpdate, TaskUpdateWithUser, TaskRead
from src.application.methods.tasks import add_task, select_all_tasks, update_task, delete_task


router_tasks = APIRouter(prefix='/api/v1/tasks', tags=['Задачи'])


@router_tasks.post("/", dependencies=[Depends(JWTBearer())], summary="Создать задачу в проекте")
async def add_task_in_project(
    task_data: TaskPydantic,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit)
) -> dict:
    try:
        app_logger.info(f"Создание новой задачи пользователем {current_user.id} в проекте {task_data.project_id}")
        result = await add_task(
            task_data=task_data,
            user_id=current_user.id,
            background_tasks=background_tasks,
            session=session
        )
        app_logger.info(f"Задача успешно создана с ID {result["success"]["task_id"]} пользователем {current_user.id}")
        return result
    except Exception as e:
        error_logger.error(f"Ошибка при создании задачи пользователем {current_user.id}: {str(e)}")
        raise


@router_tasks.get("/", dependencies=[Depends(JWTBearer())], summary="Получить все задачи по проекту")
async def get_tasks_in_projects(
    project_id: int | None = Query(None),
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit)
) -> List[TaskRead] | dict:
    try:
        app_logger.info(f"Запрос задач пользователем {current_user.id}, проект: {project_id}")
        result = await select_all_tasks(
            project_id=project_id,
            user_id=current_user.id,
            session=session
        )
        app_logger.info(f"Успешно получено {len(result)} задач для пользователя {current_user.id}")
        return result
    except Exception as e:
        error_logger.error(f"Ошибка при получении задач пользователем {current_user.id}: {str(e)}")
        raise


@router_tasks.put("/{task_id}", dependencies=[Depends(JWTBearer())], summary="Обновить существующую задачу")
async def update_task_data(
    task_id: int,
    task_data: TaskUpdate,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit)
) -> dict:
    try:
        app_logger.info(f"Обновление задачи {task_id} пользователем {current_user.id}")
        task_with_user = TaskUpdateWithUser(title=task_data.title, content=task_data.content, user_id=current_user.id)
        result = await update_task(task_id=task_id, task_data=task_with_user, session=session)
        app_logger.info(f"Задача {task_id} успешно обновлена пользователем {current_user.id}")
        return result
    except Exception as e:
        error_logger.error(f"Ошибка при обновлении задачи {task_id} пользователем {current_user.id}: {str(e)}")
        raise


@router_tasks.post("/{task_id}", dependencies=[Depends(JWTBearer())], summary="Удалить существующую задачу")
async def delete_task_in_project(
    task_id: int,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit)
) -> dict:
    try:
        app_logger.info(f"Удаление задачи {task_id} пользователем {current_user.id}")
        result = await delete_task(task_id=task_id, session=session)
        app_logger.info(f"Задача {task_id} успешно удалена пользователем {current_user.id}")
        return result
    except Exception as e:
        error_logger.error(f"Ошибка при удалении задачи {task_id} пользователем {current_user.id}: {str(e)}")
        raise