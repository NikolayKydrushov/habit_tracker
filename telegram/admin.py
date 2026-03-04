from django.contrib import admin
from .models import TelegramUser

# Register your models here.


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("user", "get_chat_id", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__username", "user__email", "user__tg_chat_id")
    readonly_fields = ("created_at", "updated_at")

    def get_chat_id(self, obj):
        return obj.user.tg_chat_id

    get_chat_id.short_description = "Chat ID"
