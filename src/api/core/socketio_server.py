import socketio
from typing import Dict, Any
from jose import JWTError, jwt
from src.utils.logger import app_logger, error_logger
from src.api.core.config import settings

# Создаем Socket.IO сервер
sio = socketio.AsyncServer(
    cors_allowed_origins=["*"],
    async_mode='asgi'
)

# Создаем ASGI приложение для Socket.IO
socket_app = socketio.ASGIApp(sio)

# Словарь для хранения подключений пользователей
user_connections: Dict[str, int] = {}


def verify_token(token: str) -> int:
    """Проверка JWT токена и извлечение user_id"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except JWTError as e:
        error_logger.error(f"JWT Error: {str(e)}")
        return None


@sio.event
async def connect(sid, environ, auth):
    try:
        app_logger.info(f"SocketIO: Попытка подключения: {sid}")

        if not auth or 'token' not in auth:
            app_logger.warning(f"SocketIO: Отсутствует токен для {sid}")
            await sio.disconnect(sid)
            return

        token = auth['token']
        user_id = verify_token(token)

        if not user_id:
            app_logger.warning(f"SocketIO: Невалидный токен для {sid}")
            await sio.disconnect(sid)
            return

        # Сохраняем подключение пользователя
        user_connections[sid] = user_id
        await sio.enter_room(sid, f"user_{user_id}")

        app_logger.info(f"SocketIO: Пользователь {user_id} подключился и присоединился к комнате уведомлений")

        # Отправляем подтверждение подключения
        await sio.emit('connected', {
            'message': 'Успешное подключение к уведомлениям',
            'user_id': user_id
        }, room=sid)

    except Exception as e:
        error_logger.error(f"SocketIO: Ошибка подключения: {str(e)}")
        await sio.disconnect(sid)


@sio.event
async def disconnect(sid):
    if sid in user_connections:
        user_id = user_connections[sid]
        del user_connections[sid]
        app_logger.info(f"SocketIO: Пользователь {user_id} отключился: {sid}")
    else:
        app_logger.info(f"SocketIO: Клиент отключился: {sid}")


async def send_task_completion_notification(user_id: int, task_data: Dict[str, Any]):
    """Отправка уведомления о завершении задачи конкретному пользователю"""
    try:
        app_logger.info(f"SocketIO: Попытка отправки уведомления пользователю {user_id}")

        room = f"user_{user_id}"
        notification_payload = {
            'task_id': task_data.get('task_id'),
            'task_title': task_data.get('task_title', 'Без названия'),
            'result_url': task_data.get('result_url'),
            'message': task_data.get('message', f'Задача "{task_data.get("task_title", "Без названия")}" завершена!')
        }

        app_logger.info(f"SocketIO: Отправка уведомления в комнату {room}: {notification_payload}")

        await sio.emit('task_completed', notification_payload, room=room)
        app_logger.info(
            f"SocketIO: Уведомление о завершении задачи {task_data.get('task_id')} отправлено пользователю {user_id}")
        return True

    except Exception as e:
        error_logger.error(f"SocketIO: Ошибка отправки уведомления пользователю {user_id}: {str(e)}")
        return False