from fastapi import APIRouter
from src.api.v1.routers.pages import router_pages
from src.api.v1.routers.projects import router_projects
from src.api.v1.routers.tasks import router_tasks
from src.api.v1.routers.users import router_auth


main_router = APIRouter()

main_router.include_router(router_pages)
main_router.include_router(router_projects)
main_router.include_router(router_tasks)
main_router.include_router(router_auth)