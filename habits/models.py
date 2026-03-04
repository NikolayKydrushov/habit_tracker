from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

from habits.validators import validate_habit

User = get_user_model()


class Habit(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    place = models.CharField(max_length=255, verbose_name="Место")
    time = models.TimeField(verbose_name="Время выполнения")
    action = models.TextField(verbose_name="Действие")
    is_pleasant = models.BooleanField(default=False, verbose_name="Приятная привычка")
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_to",
        verbose_name="Связанная привычка",
        limit_choices_to={"is_pleasant": True},
    )
    reward = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Вознаграждение"
    )
    execution_time = models.PositiveIntegerField(
        verbose_name="Время на выполнение (сек)",
        help_text="Не более 120 секунд",
        validators=[
            MaxValueValidator(
                120, message="Время выполнения не может превышать 120 секунд."
            )
        ],
    )
    periodicity = models.PositiveIntegerField(
        default=1,
        verbose_name="Периодичность (дни)",
        help_text="Не реже 1 раза в 7 дней",
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )
    is_public = models.BooleanField(default=False, verbose_name="Публичность")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]  # Сортировка по умолчанию
        indexes = [
            models.Index(fields=["user", "is_public"]),  # Индекс для частых запросов
            models.Index(fields=["time"]),  # Индекс для поиска по времени (Celery)
        ]

    def clean(self):
        validate_habit(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} в {self.place} в {self.time}"
