import time
from datetime import datetime
import httpx
from src.api.core.config import settings
from src.utils.logger import error_logger


async def get_moscow_time() -> datetime:
    start_time = time.time()
    api_key = settings.API_KEY_ABSTRACT_API
    url = f"https://timezone.abstractapi.com/v1/current_time/?api_key={api_key}&location=Moscow, Russia"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            naive_datetime = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M:%S")
            return naive_datetime

    except httpx.TimeoutException as e:
        execution_time = time.time() - start_time
        error_logger.error(f"Timeout при запросе к AbstractAPI: {str(e)} за {execution_time:.3f}с")
        raise
    except httpx.HTTPStatusError as e:
        execution_time = time.time() - start_time
        error_logger.error(
            f"HTTP ошибка при запросе к AbstractAPI: {e.response.status_code} - {str(e)} за {execution_time:.3f}с")
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        error_logger.error(f'Ошибка генерации московского времени: {str(e)} за {execution_time:.3f}с')
        raise