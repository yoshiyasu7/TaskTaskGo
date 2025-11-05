from fastapi import Depends, status, HTTPException
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.core.security import get_password_hash, authenticate_user, create_access_token
from src.api.v1.schemas import UsernamePydantic, TokenPydantic
from src.api.v1.schemas.users import UserRegister
from src.infrastructure.database.dao import UserDAO
from src.infrastructure.database.session import get_session_with_commit, get_session_without_commit


async def add_user(user_data: UserRegister, session: AsyncSession = Depends(get_session_with_commit)):
    existing_users = await UserDAO(session).find_all_by_filters(
        filters=UsernamePydantic(username=user_data.username)
    )
    if existing_users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким username уже существует"
        )
    user_dict = user_data.model_dump()
    user_dict["password"] = get_password_hash(user_data.password)
    new_user = await UserDAO(session).add(UserRegister(**user_dict))
    return {"message": "Вы успешно зарегистрированы!", "user_id": {new_user.id}}


async def select_user(
    user_data: UserRegister,
    session: AsyncSession = Depends(get_session_without_commit)
) -> TokenPydantic:

    user = await UserDAO(session).find_one_or_none(filters=UsernamePydantic(username=user_data.username))
    if not (user and await authenticate_user(user=user, password=user_data.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный логин или пароль"
        )
    access_token = create_access_token({'sub': str(user.id)})
    return TokenPydantic(access_token=access_token, token_type="bearer")


async def update_username(user_id: int, new_username: str, session: AsyncSession = Depends(get_session_with_commit)):
    ValueModel = create_model('ValueModel', username=(str, ...))
    await UserDAO(session).update_one_by_id(data_id=user_id, values=ValueModel(username=new_username))


async def delete_user_by_id(user_id: int, session: AsyncSession = Depends(get_session_with_commit)):
    filter_criteria = create_model('FilterModel', user_id=(int, ...))
    await UserDAO(session).delete_by_filters(filters=filter_criteria(user_id=user_id))