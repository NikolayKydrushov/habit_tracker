from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка для кастомной модели пользователя."""

    list_display = ("username", "email", "tg_chat_id", "is_staff")
    fieldsets = UserAdmin.fieldsets + (("Telegram", {"fields": ("tg_chat_id",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Telegram", {"fields": ("tg_chat_id",)}),
    )
