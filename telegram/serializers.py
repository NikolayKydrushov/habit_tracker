from rest_framework import serializers
from .models import TelegramUser


class TelegramLinkSerializer(serializers.Serializer):
    tg_chat_id = serializers.CharField(max_length=50)

    def validate_tg_chat_id(self, value):
        """Проверяет, что chat_id состоит из цифр."""
        if not value.isdigit():
            raise serializers.ValidationError("ID чата должен содержать только цифры.")
        return value
