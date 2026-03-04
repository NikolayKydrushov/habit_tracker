import asyncio
import logging
from aiogram import Bot
from django.conf import settings

logger = logging.getLogger(__name__)

if settings.TELEGRAM_BOT_TOKEN:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
else:
    bot = None
    logger.warning("TELEGRAM_BOT_TOKEN не указан. Telegram-интеграция отключена.")


async def send_telegram_message(chat_id: str, text: str) -> bool:
    """
    Отправляет сообщение через Telegram Bot API.
    Возвращает True при успешной отправке, False при ошибке.
    """
    if not bot:
        logger.error("Telegram бот не инициализирован. Проверьте TELEGRAM_BOT_TOKEN.")
        return False

    try:
        await bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Сообщение успешно отправлено в чат {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram (chat_id: {chat_id}): {e}")
        return False


def send_message_sync(chat_id: str, text: str) -> bool:
    """Синхронная обёртка для отправки сообщений."""
    try:
        # Создаём новый цикл событий, если его нет
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(send_telegram_message(chat_id, text))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Ошибка в синхронной отправке: {e}")
        return False
