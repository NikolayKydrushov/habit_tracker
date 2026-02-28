from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from .models import Habit
from telegram.services import send_habit_reminder_to_user
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_and_send_habit_reminders():
    """
    Задача Celery для проверки и отправки напоминаний о привычках.
    Запускается периодически (каждую минуту).
    """
    current_time = timezone.now()
    current_hour = current_time.hour
    current_minute = current_time.minute

    logger.info(f"Проверка напоминаний на {current_hour}:{current_minute}")

    # Находим привычки, которые нужно выполнить в текущее время
    # Исключаем приятные привычки (о них не напоминаем)
    habits_to_remind = Habit.objects.filter(
        time__hour=current_hour,
        time__minute=current_minute,
        is_pleasant=False,  # Напоминаем только о полезных привычках
        user__tg_chat_id__isnull=False,  # Только пользователи с привязанным Telegram
    ).select_related('user')

    if not habits_to_remind.exists():
        logger.info("Нет привычек для напоминания в текущее время")
        return "Нет привычек для напоминания"

    # Группируем привычки по пользователям для эффективной отправки
    user_habits = {}
    for habit in habits_to_remind:
        # Проверяем периодичность
        days_since_created = (current_time.date() - habit.created_at.date()).days
        if days_since_created % habit.periodicity == 0:
            user_id = habit.user.id
            if user_id not in user_habits:
                user_habits[user_id] = {
                    'user': habit.user,
                    'habits': []
                }
            user_habits[user_id]['habits'].append(habit)

    # Отправляем напоминания каждому пользователю
    total_sent = 0
    for user_data in user_habits.values():
        try:
            # Вызываем синхронную функцию отправки
            # Celery сам создает асинхронность на уровне задач
            sent = send_habit_reminder_to_user(
                user=user_data['user'],
                habits=user_data['habits']
            )
            total_sent += sent
            logger.info(f"Отправлено {sent} напоминаний пользователю {user_data['user'].username}")
        except Exception as e:
            logger.error(f"Ошибка при отправке напоминаний пользователю {user_data['user'].username}: {e}")

    return f"Отправлено напоминаний: {total_sent}"


# Альтернативный вариант: создаем отдельную задачу для каждого пользователя
@shared_task
def send_user_habit_reminders(user_id, habit_ids):
    """
    Отправляет напоминания конкретному пользователю о конкретных привычках.
    """
    from django.contrib.auth import get_user_model
    from .models import Habit

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        habits = Habit.objects.filter(id__in=habit_ids)

        sent = send_habit_reminder_to_user(user=user, habits=list(habits))
        return f"Отправлено {sent} напоминаний пользователю {user.username}"
    except Exception as e:
        logger.error(f"Ошибка в задаче send_user_habit_reminders: {e}")
        return f"Ошибка: {str(e)}"