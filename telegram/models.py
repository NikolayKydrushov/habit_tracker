from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


class TelegramUser(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='telegram_user'
    )
    username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Username в Telegram"
    )
    first_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Имя в Telegram"
    )
    last_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Фамилия в Telegram"
    )

    notification_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Предпочтительное время уведомлений",
        help_text="Если не указано, используются времена привычек"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Получает уведомления"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Telegram‑пользователь"
        verbose_name_plural = "Telegram‑пользователи"

    def __str__(self):
        chat_id = self.user.tg_chat_id or "не привязан"
        return f"{self.user.username} — {chat_id}"

    def get_chat_id(self):
        """Получить chat_id из связанного пользователя."""
        return self.user.tg_chat_id
