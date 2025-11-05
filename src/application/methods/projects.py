from typing import List

from fastapi import Depends
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas import ProjectCreate, ProjectFilter, ProjectRead
from src.infrastructure.database.dao import ProjectDAO
from src.infrastructure.database.session import get_session_with_commit, get_session_without_commit
from src.utils.logger import app_logger


async def add_project(project_data: ProjectCreate, session: AsyncSession = Depends(get_session_with_commit)):
    new_project = await ProjectDAO(session).add(project_data)
    app_logger.info(f"Добавлен новый проект с ID: {new_project.id}")
    return {"message": "ok", "project_id": new_project.id}


async def select_all_projects(
    project_id: int,
    user_id: int,
    session: AsyncSession = Depends(get_session_without_commit)
) -> List[ProjectRead] | dict:

    filters_dict = {'user_id': user_id}
    if project_id:
        filters_dict['id'] = project_id

    projects = await ProjectDAO(session).find_all_by_filters(filters=ProjectFilter(**filters_dict))
    if projects:
        return [ProjectRead.model_validate(project).model_dump(by_alias=True) for project in projects]
    return {'message': f'Проекты не найдены или у вас нет доступа к ним!'}


async def update_project(project_id: int, project_data: ProjectCreate, session: AsyncSession = Depends(get_session_with_commit)):
    ValueModel = create_model('ValueModel', title=(str, None), content=(str, None), )
    filters_dict = {}
    if project_data.title:
        filters_dict['title'] = project_data.title
    if project_data.content:
        filters_dict['content'] = project_data.content

    await ProjectDAO(session).update_one_by_id(data_id=project_id, values=ValueModel(**filters_dict))
    return {"message": "Проект обновлён"}


async def delete_project(project_id: int, session: AsyncSession = Depends(get_session_with_commit)):
    filter_criteria = create_model('FilterModel', id=(int, ...))
    await ProjectDAO(session).delete_by_filters(filters=filter_criteria(id=project_id))