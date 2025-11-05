from src.infrastructure.database.base import BaseDAO
from src.domain.models.all_models import User, Project, Task


class UserDAO(BaseDAO[User]):
    model = User


class ProjectDAO(BaseDAO[Project]):
    model = Project


class TaskDAO(BaseDAO[Task]):
    model = Task