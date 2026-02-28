import logging
from typing import Optional, List
from .bot import send_message_sync
from .models import TelegramUser
from habits.models import Habit

logger = logging.getLogger(__name__)


def format_habit_reminder(habit: Habit) -> str:
    """Формирует текст напоминания о привычке."""
    time_str = habit.time.strftime("%H:%M")

    message = (
        f"<b>Напоминание о привычке!</b>\n\n"
        f"<b>Действие:</b> {habit.action}\n"
        f"<b>Место:</b> {habit.place}\n"
        f"<b>Время:</b> {time_str}\n"
        f"<b>Длительность:</b> {habit.execution_time} сек.\n"
    )

    if habit.related_habit:
        message += f"<b>После:</b> {habit.related_habit.action}"
    elif habit.reward:
        message += f"<b>Вознаграждение:</b> {habit.reward}"

    return message


def send_habit_reminder_to_user(user, habits: List[Habit]) -> int:
    """
    Отправляет напоминания о привычках конкретному пользователю.
    Возвращает количество отправленных сообщений.
    """
    if not user.tg_chat_id:
        logger.warning(f"Пользователь {user.username} не имеет chat_id")
        return 0

    # Проверяем, активен ли Telegram-профиль
    try:
        telegram_profile = user.telegram_profile
        if not telegram_profile.is_active:
            logger.info(f"Telegram-профиль пользователя {user.username} неактивен")
            return 0
    except TelegramUser.DoesNotExist:
        # Создаём профиль, если его нет (по умолчанию активен)
        telegram_profile = TelegramUser.objects.create(user=user)

    sent_count = 0
    for habit in habits:
        message = format_habit_reminder(habit)
        success = send_message_sync(user.tg_chat_id, message)
        if success:
            sent_count += 1
            logger.debug(f"Отправлено напоминание о привычке {habit.id} пользователю {user.username}")
        else:
            logger.error(f"Не удалось отправить напоминание о привычке {habit.id} пользователю {user.username}")

    return sent_count


def get_active_telegram_users():
    """Возвращает активных пользователей с привязанным Telegram."""
    return TelegramUser.objects.filter(
        is_active=True,
        user__tg_chat_id__isnull=False
    ).select_related('user')


def send_habit_reminders(habits: Optional[List[Habit]] = None) -> int:
    """
    Отправляет напоминания всем активным пользователям.
    Возвращает общее количество отправленных сообщений.
    """
    total_sent = 0
    telegram_users = get_active_telegram_users()

    for tg_user in telegram_users:
        user = tg_user.user

        if habits is None:
            user_habits = Habit.objects.filter(user=user)
        else:
            user_habits = [h for h in habits if h.user_id == user.id]

        if user_habits:
            sent = send_habit_reminder_to_user(user, user_habits)
            total_sent += sent

    logger.info(f"Отправлено всего напоминаний: {total_sent}")
    return total_sent


def test_telegram_connection(chat_id: str) -> bool:
    """Отправляет тестовое сообщение для проверки связи."""
    test_message = (
        "<b>Подключение к Habit Tracker установлено!</b>\n\n"
        "Теперь вы будете получать уведомления о своих привычках."
    )
    return send_message_sync(chat_id, test_message)