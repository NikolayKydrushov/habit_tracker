from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_reward_and_related_habit(habit):
    """Нельзя одновременно указывать вознаграждение и связанную привычку."""
    if habit.reward and habit.related_habit:
        raise ValidationError(
            "Нельзя одновременно указать вознаграждение и связанную привычку."
        )

def validate_execution_time(habit):
    """Время выполнения не должно превышать 120 секунд."""
    if habit.execution_time > 120:
        raise ValidationError(
            "Время выполнения не может быть больше 120 секунд."
        )

def validate_related_habit_is_pleasant(habit):
    """В связанные привычки могут попадать только приятные привычки."""
    if habit.related_habit and not habit.related_habit.is_pleasant:
        raise ValidationError(
            "Связанная привычка должна быть приятной."
        )

def validate_pleasant_habit_restrictions(habit):
    """У приятной привычки не может быть вознаграждения или связанной привычки."""
    if habit.is_pleasant and (habit.reward or habit.related_habit):
        raise ValidationError(
            "Приятная привычка не может иметь вознаграждения или связанной привычки."
        )

def validate_periodicity(habit):
    """Периодичность не должна превышать 7 дней."""
    if habit.periodicity > 7:
        raise ValidationError(
            "Периодичность не может быть больше 7 дней."
        )

def validate_habit(habit):
    """Общий валидатор для привычки."""
    validators = [
        validate_reward_and_related_habit,
        validate_execution_time,
        validate_related_habit_is_pleasant,
        validate_pleasant_habit_restrictions,
        validate_periodicity,
    ]
    for validator in validators:
        validator(habit)
