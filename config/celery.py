import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("habit_tracker")

# Загружаем конфигурацию из настроек Django, используя префикс CELERY
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически обнаруживаем задачи в приложениях
app.autodiscover_tasks()

# Настройка периодических задач (можно и в settings.py, но здесь нагляднее)
app.conf.beat_schedule = {
    "send-habit-reminders-every-minute": {
        "task": "habits.tasks.check_and_send_habit_reminders",
        "schedule": crontab(minute="*/1"),  # Каждую минуту
        "options": {
            "expires": 60,  # Задача "протухает" через 60 секунд
        },
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
