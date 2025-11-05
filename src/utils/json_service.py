import time
from typing import Dict, Any
import httpx
from src.utils.logger import error_logger
from src.api.core.config import settings


async def create_json_for_task(data: Dict[str, Any]):
    start_time = time.time()
    url = 'https://api.jsonbin.io/v3/b'
    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': f'{settings.X_MASTER_KEY}'
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException as e:
        execution_time = time.time() - start_time
        error_logger.error(f"Timeout при запросе к JSON API: {str(e)} за {execution_time:.3f}с")
        raise
    except httpx.HTTPStatusError as e:
        execution_time = time.time() - start_time
        error_logger.error(
            f"HTTP ошибка при запросе к JSON API: {e.response.status_code} - {str(e)} за {execution_time:.3f}с")
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        error_logger.error(f'Ошибка генерации JSON: {str(e)} за {execution_time:.3f}с')
        raise