import os
from loguru import logger
from src.utils.telegram_notifier import send_telegram_message_sync
from src.api.core.config import settings

# Удаляем стандартный обработчик loguru
logger.remove()

# Настройка консольного вывода
logger.add(
    sink=lambda msg: print(msg, end=""),
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True
)

# Настройка ежедневных файлов логов с автоматическим удалением
logger.add(
    sink=os.path.join(f"{settings.BASE_DIR}/logs", f"{settings.LOG_FILE_PREFIX}_{{time:YYYY-MM-DD}}.log"),
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="00:00",  # Ротация в полночь
    retention=f"{settings.LOG_RETENTION_DAYS} days",  # Хранение файлов N дней
    compression="zip",  # Сжатие старых файлов
    encoding="utf-8"
)

# Создаем отдельные логгеры для разных типов сообщений
app_logger = logger.bind(type="app")
error_logger = logger.bind(type="error")
db_logger = logger.bind(type="database")


def _telegram_sink(message):
    record = message.record

    def _escape_html(s: str) -> str:
        try:
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        except Exception:
            return s

    exc = record.get("exception")
    exc_name = getattr(getattr(exc, "type", None), "__name__", "") if exc else ""

    extra = record.get("extra") or {}
    method = extra.get("method")
    path = extra.get("path")

    parts = [
        "<b>🚨 Ошибка в TaskTaskGo</b>",
        f"<b>Уровень</b>: {record['level'].name}",
        f"<b>Место</b>: {record['name']}:{record['function']}:{record['line']}",
    ]
    if method or path:
        parts.append(f"<b>Запрос</b>: {(method or '')} {(path or '')}".strip())
    if exc_name:
        parts.append(f"<b>Исключение</b>: {exc_name}")
    if record["message"]:
        parts.append(f"<b>Сообщение</b>: {_escape_html(record['message'])}")

    text = "\n".join(parts)

    try:
        send_telegram_message_sync(text)
    except Exception:
        pass


logger.add(_telegram_sink, level="ERROR", backtrace=True, diagnose=False, enqueue=True)