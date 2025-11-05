from typing import List

from fastapi import BackgroundTasks, Depends
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas import TaskPydantic, ProjectFilter
from src.api.v1.schemas.tasks import TaskUpdate, TaskUpdateWithUser, TaskRead
from src.application.services.task_proccessing_service import TaskProcessingService
from src.infrastructure.database.dao import TaskDAO, ProjectDAO
from src.infrastructure.database.session import get_session_with_commit, get_session_without_commit


async def add_task(
        task_data: TaskPydantic,
        user_id: int,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_session_with_commit),
):
    task_data_with_user = TaskPydantic(
        title=task_data.title, content=task_data.content, project_id=task_data.project_id, user_id=user_id
    )
    new_task = await TaskDAO(session).add(task_data_with_user)

    # Подготовка данных для фоновой обработки
    task_processing_data = {
        "id": new_task.id,
        "title": new_task.title,
        "content": new_task.content,
        "project_id": new_task.project_id,
        "user_id": new_task.user_id,
        "created_at": new_task.created_at.isoformat(),
    }
    # Запуск фоновой обработки через сервис
    processing_service = TaskProcessingService()
    background_tasks.add_task(
        processing_service.process_task_background,
        new_task.id,
        task_processing_data,
        session
    )
    return {"success": {"task_id": new_task.id}}


async def select_all_tasks(
    project_id: int,
    user_id: int,
    session: AsyncSession = Depends(get_session_without_commit)
) -> List[TaskRead] | dict:

    filters_project_dict = {'user_id': user_id}
    if project_id:
        filters_project_dict['id'] = project_id

    project = await ProjectDAO(session).find_all_by_filters(filters=ProjectFilter(**filters_project_dict))
    if not project:
        return {'message': f'Проект с ID {project_id} не найден или у вас нет доступа к нему!'}

    tasks_filters = create_model('TasksFilter', user_id=(int, ...), project_id=(int, None), title=(str, None))
    filters_dict = {'user_id': user_id}
    if project_id:
        filters_dict['project_id'] = project_id

    tasks = await TaskDAO(session).find_all_by_filters(filters=tasks_filters(**filters_dict))
    return [TaskRead.model_validate(task, from_attributes=True).model_dump() for task in tasks]


async def update_task(task_id: int, task_data: TaskUpdateWithUser, session: AsyncSession = Depends(get_session_with_commit)):
    ValueModel = create_model('ValueModel', title=(str, None), status=(str, None), content=(str, None))
    filters_dict = {}
    if task_data.title:
        filters_dict['title'] = task_data.title
    if task_data.status:
        filters_dict['status'] = task_data.status
    if task_data.content:
        filters_dict['content'] = task_data.content

    await TaskDAO(session).update_one_by_id(data_id=task_id, values=ValueModel(**filters_dict))
    return {"message": "Задача обновлена", "task_id": task_id}


async def delete_task(task_id: int, session: AsyncSession = Depends(get_session_with_commit)):
    filter_criteria = create_model('FilterModel', id=(int, ...))
    await TaskDAO(session).delete_by_filters(filters=filter_criteria(id=task_id))
    return {"message": "Задача удалена"}