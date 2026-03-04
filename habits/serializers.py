from rest_framework import serializers
from .models import Habit
from .validators import validate_habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "reward",
            "execution_time",
            "periodicity",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

        def validate(self, data):
            """Применяем кастомные валидаторы."""
            # Создаем временный объект для валидации
            habit = Habit(**data)

            # Если есть related_habit, нужно получить его из БД
            if "related_habit" in data and data["related_habit"]:
                # Т.к. related_habit может быть передан как ID, нам нужно получить объект
                # Но в validate мы работаем только с данными, поэтому
                # используем отдельный метод валидации
                pass

            # Применяем все валидаторы
            validate_habit(habit)

            return data

        def validate_related_habit(self, value):
            """Дополнительная валидация связанной привычки."""
            if value and not value.is_pleasant:
                raise serializers.ValidationError(
                    "Связанная привычка должна быть приятной."
                )
            return value
