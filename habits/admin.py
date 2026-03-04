from django.contrib import admin
from .models import Habit

# Register your models here.


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "time", "is_pleasant", "is_public", "periodicity")
    list_filter = ("is_pleasant", "is_public", "user")
    search_fields = ("action", "place", "user__username")
    raw_id_fields = ("user", "related_habit")
    fieldsets = (
        ("Основное", {"fields": ("user", "place", "time", "action")}),
        (
            "Характеристики",
            {"fields": ("is_pleasant", "is_public", "periodicity", "execution_time")},
        ),
        (
            "Вознаграждение",
            {
                "fields": ("reward", "related_habit"),
                "description": "Укажите либо вознаграждение, либо связанную привычку",
            },
        ),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at")
