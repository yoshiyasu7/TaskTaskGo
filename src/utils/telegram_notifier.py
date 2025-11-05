import httpx
from src.api.core.config import settings

def send_telegram_message_sync(text: str) -> None:
    """
    Синхронная отправка в Telegram Bot API. Вызывается из loguru sink.
    """
    if not settings.TG_BOT_TOKEN or not settings.TG_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    # Синхронный клиент, чтобы вызывать из синка без event loop
    with httpx.Client(timeout=5.0) as client:
        client.post(url, json=payload)