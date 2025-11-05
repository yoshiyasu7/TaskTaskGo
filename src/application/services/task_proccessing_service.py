import time
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.logger import error_logger, app_logger
from src.api.core.socketio_server import send_task_completion_notification
from src.api.v1.schemas.tasks import TaskResultURL
from src.infrastructure.database.dao import TaskDAO
from src.infrastructure.s3storage.client import S3Client
from src.utils.json_service import create_json_for_task
from src.api.core.config import settings


class TaskProcessingService:
    def __init__(self):
        self.s3_client = S3Client()

    async def process_task_background(
            self,
            task_id: int,
            task_data: Dict[str, Any],
            session: AsyncSession
    ) -> None:
        """ Генерация JSON и загрузка в S3 """
        start_time = time.time()
        try:
            app_logger.info(f"Начата фоновая обработка задачи {task_id}")

            # 1. Генерация JSON через внешний API
            generated_json = await create_json_for_task(task_data)

            # 2. Загрузка в S3
            result_url = await self._upload_to_s3(generated_json, task_id)

            # 3. Обновление записи задачи с URL результата
            await self._update_task_result(task_id, result_url, session)

            # 4. Отправка уведомления через SocketIO
            user_id = task_data.get('user_id')
            if not user_id:
                app_logger.error(f"Не удалось получить user_id для задачи {task_id}")
                return

            notification_data = {
                'task_id': task_id,
                'task_title': task_data.get('title', 'Без названия'),
                'result_url': result_url,
                'message': f'Задача "{task_data.get("title", "Без названия")}" успешно завершена! Результат доступен для скачивания.'
            }

            success = await send_task_completion_notification(user_id, notification_data)

            if success:
                app_logger.info(f"Уведомление для задачи {task_id} отправлено пользователю {user_id}")
            else:
                app_logger.warning(f"Пользователь {user_id} не подключен к уведомлениям для задачи {task_id}")

            execution_time = time.time() - start_time
            app_logger.info(f"Задача {task_id} успешно обработана за {execution_time:.3f}с")

        except Exception as e:
            execution_time = time.time() - start_time
            error_logger.error(f"Ошибка при фоновой обработке задачи {task_id}: {str(e)} за {execution_time:.3f}с")
            raise

    async def _upload_to_s3(self, json_data: Dict[str, Any], task_id: int) -> str:
        """ Загрузка в S3 и получение url """
        object_name = f"tasks/task_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        await self.s3_client.upload_json(json_data, object_name, indent=2)
        return f"{settings.AWS_ENDPOINT_URL}/{settings.AWS_BUCKET}/{object_name}"

    async def _update_task_result(self, task_id: int, result_url: str, session: AsyncSession):
        """ Обновление поля result_url в задаче """
        await TaskDAO(session).update_one_by_id(task_id, TaskResultURL(result_url=result_url))
        await session.commit()