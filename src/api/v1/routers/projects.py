from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.logger import app_logger, error_logger
from src.infrastructure.database.session import get_session_with_commit
from src.api.core.security import get_current_user, JWTBearer
from src.api.v1.schemas.projects import ProjectCreate, ProjectUpdate, ProjectRead
from src.application.methods.projects import (
    add_project, select_all_projects, update_project, delete_project
)


router_projects = APIRouter(prefix='/api/v1/projects', tags=['Проекты'])


@router_projects.post("/", dependencies=[Depends(JWTBearer())], summary="Создать новый проект")
async def add_new_project(
    project_data: ProjectUpdate,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit)
) -> dict:
    try:
        app_logger.info(f"Создание нового проекта пользователем {current_user.id}")
        project_with_user = ProjectCreate(title=project_data.title, content=project_data.content,
                                          user_id=current_user.id)
        result = await add_project(project_data=project_with_user, session=session)
        app_logger.info(f"Проект успешно создан с ID {result["project_id"]}, пользователем {current_user.id}")
        return result
    except Exception as e:
        error_logger.error(f"Ошибка при создании проекта пользователем {current_user.id}: {str(e)}")
        raise


@router_projects.get("/", dependencies=[Depends(JWTBearer())], summary="Получить все проекты")
async def get_all_projects(
    project_id: int = None,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit)
) -> List[ProjectRead] | dict:
    try:
        app_logger.info(f"Запрос всех проектов пользователем {current_user.id}")
        result = await select_all_projects(project_id=project_id, user_id=current_user.id, session=session)
        app_logger.info(f"Успешно получено {len(result)} проектов для пользователя {current_user.id}")
        return result
    except Exception as e:
        error_logger.error(f"Ошибка при получении проектов пользователя {current_user.id}: {str(e)}")
        raise


@router_projects.put("/{project_id}", dependencies=[Depends(JWTBearer())], summary="Обновить существующий проект")
async def update_project_data(
    project_id: int,
    project_data: ProjectUpdate,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit)
) -> dict:
    try:
        app_logger.info(f"Обновление проекта {project_id} пользователем {current_user.id}")
        project_with_user = ProjectCreate(title=project_data.title, content=project_data.content, user_id=current_user.id)
        result = await update_project(project_id=project_id, project_data=project_with_user, session=session)
        app_logger.info(f"Проект {project_id} успешно обновлен пользователем {current_user.id}")
        return result
    except Exception as e:
        error_logger.error(f"Ошибка при обновлении проекта {project_id} пользователем {current_user.id}: {str(e)}")
        raise


@router_projects.post("/{project_id}", dependencies=[Depends(JWTBearer())], summary="Удалить существующий проект")
async def delete_project_router(
    project_id: int,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit)
) -> dict:
    try:
        app_logger.info(f"Удаление проекта {project_id} пользователем {current_user.id}")
        result = await delete_project(project_id=project_id, session=session)
        app_logger.info(f"Проект {project_id} успешно удалён пользователем {current_user.id}")
        return {"message": "Проект удалён"}
    except Exception as e:
        error_logger.error(f"Ошибка при удалении проекта {project_id} пользователем {current_user.id}: {str(e)}")
        raise