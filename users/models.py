from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    tg_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="ID чата в Telegram для рассылок",
    )

    # Переопределяем поля с указанием related_name
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to.",
        related_name="custom_user_set",  # уникальное имя
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_user_permissions_set",  # уникальное имя
        related_query_name="user",
    )

    def __str__(self):
        return self.username
