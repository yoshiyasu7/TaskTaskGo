from fastapi import APIRouter, Request, Path, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router_pages = APIRouter(prefix='', tags=['Страницы'])
templates = Jinja2Templates(directory='templates')


@router_pages.get("/notifications", response_class=HTMLResponse, summary="Страница уведомлений")
async def notifications_page(request: Request):
    return templates.TemplateResponse("users/socketio_client.html", {"request": request})


@router_pages.get("/register", response_class=HTMLResponse, summary="Страница регистрации")
async def register_page(request: Request):
    return templates.TemplateResponse("users/register.html", {"request": request})


@router_pages.get("/login", response_class=HTMLResponse, summary="Страница входа в аккаунт")
async def login_page(request: Request):
    return templates.TemplateResponse("users/login.html", {"request": request})


@router_pages.get("/profile", response_class=HTMLResponse, summary="Профиль пользователя")
async def profile_page(request: Request):
    return templates.TemplateResponse("users/profile.html", {"request": request})


@router_pages.get("/logout", response_class=HTMLResponse, summary="Страница выхода из аккаунта")
async def profile_page(request: Request):
    return templates.TemplateResponse("users/logout.html", {"request": request})


@router_pages.get("/projects/create", response_class=HTMLResponse, summary="Создать проект")
async def project_create_page(request: Request):
    return templates.TemplateResponse("projects/project_create.html", {"request": request})


@router_pages.get("/projects/{project_id}/edit", response_class=HTMLResponse, summary="Редактирование проекта")
async def project_edit_page(request: Request, project_id: int = Path(...)):
    return templates.TemplateResponse("projects/project_edit.html", {"request": request, "project_id": project_id})


@router_pages.get("/projects/{project_id}/delete", response_class=HTMLResponse, summary="Удаление проекта")
async def project_delete_page(request: Request, project_id: int = Path(...)):
    return templates.TemplateResponse("projects/project_delete.html", {"request": request, "project_id": project_id})


@router_pages.get("/tasks/create", response_class=HTMLResponse, summary="Создать задачу")
async def task_create_page(request: Request, project_id: int | None = Query(None)):
    return templates.TemplateResponse("tasks/task_create.html", {"request": request, "project_id": project_id})


@router_pages.get("/tasks/{task_id}/edit", response_class=HTMLResponse, summary="Редактирование задачи")
async def task_edit_page(request: Request, task_id: int = Path(...)):
    return templates.TemplateResponse("tasks/task_edit.html", {"request": request, "task_id": task_id})


@router_pages.get("/tasks/{task_id}/delete", response_class=HTMLResponse, summary="Удаление задачи")
async def task_delete_page(request: Request, task_id: int = Path(...)):
    return templates.TemplateResponse("tasks/task_delete.html", {"request": request, "task_id": task_id})