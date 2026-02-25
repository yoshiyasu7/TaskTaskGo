from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.session import get_session_with_commit, get_session_without_commit
from src.api.core.security import get_current_user, JWTBearer
from src.api.v1.schemas.users import TokenPydantic, UserRegister, UserOut
from src.application.methods.users import select_user, add_user
from src.utils.logger import app_logger, error_logger

router_auth = APIRouter(prefix='/api/v1/auth', tags=['Вход и регистрация'])


@router_auth.post("/register/", summary="Регистрация аккаунта")
async def register_user(user_data: UserRegister, session: AsyncSession = Depends(get_session_with_commit)) -> dict:
    app_logger.info(f"Запрос на регистрацию нового пользователя: {user_data.username}")
    try:
        result = await add_user(user_data=user_data, session=session)
        app_logger.info(f"Пользователь успешно зарегистрирован: {result['user_id']}")
        return result
    except Exception as e:
        error_logger.error(f"Ошибка регистрации пользователя {user_data.username}: {str(e)}")
        raise


@router_auth.post("/login/", summary="Вход в аккаунт")
async def login_user(user_data: UserRegister, session: AsyncSession = Depends(get_session_without_commit)) -> TokenPydantic:
    app_logger.info(f"Запрос входа пользователя: {user_data.username}")
    try:
        result = await select_user(user_data=user_data, session=session)
        app_logger.info(f"Пользователь успешно вошел в систему: {user_data.username}")
        return result
    except Exception as e:
        error_logger.error(f"Ошибка входа пользователя {user_data.username}: {str(e)}")
        raise


@router_auth.get(
    "/user/",
    response_model=UserOut,
    dependencies=[Depends(JWTBearer())],
    summary="Получить информацию о текущем пользователе"
)
async def get_current_user_info(current_user: UserOut = Depends(get_current_user)):
    app_logger.info(f"Запрос информации о текущем пользователе: {current_user.id}")
    try:
        app_logger.info(f"Информация о пользователе успешно получена: {current_user.id}")
        return current_user
    except Exception as e:
        error_logger.error(f"Ошибка получения информации о пользователе: {str(e)}")
        raise


@router_auth.post("/logout/", dependencies=[Depends(JWTBearer())], summary="Выход из аккаунта")
async def logout_user(current_user = Depends(get_current_user)):
    app_logger.info(f"Запрос выхода пользователя: {getattr(current_user, 'email', 'Unknown')}")
    try:
        app_logger.info(f"Пользователь успешно вышел из системы: {getattr(current_user, 'email', 'Unknown')}")
        return {'message': 'Вы вышли из аккаунта'}
    except Exception as e:
        error_logger.error(f"Ошибка при выходе пользователя: {str(e)}")
        raise