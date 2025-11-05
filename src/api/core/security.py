from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from src.utils.logger import app_logger, error_logger
from src.api.core.config import settings
from src.infrastructure.database.dao import UserDAO
from src.infrastructure.database.session import get_session_without_commit
from src.api.v1.schemas import UserIDPydantic

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(user, password):
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        return None
    app_logger.info(f"Аутентификация пользователя прошла успешно: {user.username}")
    return user


def create_access_token(data: dict) -> str:
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(hours=12)
        to_encode.update({'exp': expire})
        encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        app_logger.info(f"Access token создан для пользователя: {data.get('sub')}")
        return encode_jwt
    except Exception as e:
        error_logger.error(f"Ошибка создания токена: {str(e)}")
        raise


def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token.get('sub')
    except JWTError as e:
        error_logger.error(f"Ошибка декодирования токена: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Токен невалиден или истёк')


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                error_logger.warning("Невалидная схема авторизации")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Невалидная схема авторизации')
            if not self.verify_jwt(credentials.credentials):
                error_logger.warning("Невалидный JWT токен")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Невалидный токен')

            return credentials.credentials
        else:
            error_logger.warning("Невалидный JWT код авторизации")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Невалидный код авторизации')

    def verify_jwt(self, jwtoken: str) -> bool:
        is_token_valid: bool = False
        try:
            payload = decode_access_token(jwtoken)
            if payload:
                is_token_valid = True
        except Exception as e:
            error_logger.error(f"Ошибка верификации JWT: {str(e)}")
        return is_token_valid


async def get_current_user(
        token: str = Depends(JWTBearer()),
        session: AsyncSession = Depends(get_session_without_commit)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get('sub')
        if not user_id:
            error_logger.error("ID пользователя не найден в payload токена")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='ID пользователя не найден')

        user = await UserDAO(session).find_one_or_none(filters=UserIDPydantic(id=int(user_id)))
        if not user:
            error_logger.error(f"Пользователь не найден в базе данных: {user_id}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователь с таким ID не найден')

        app_logger.info(f"Пользователь успешно получен: {user.id}")
        return user

    except JWTError as e:
        error_logger.error(f"Ошибка декодирования JWT в get_current_user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валиден')
    except Exception as e:
        error_logger.error(f"Неожиданная ошибка в get_current_user: {str(e)}")
        raise