from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import TelegramLinkSerializer
from .models import TelegramUser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .services import test_telegram_connection

User = get_user_model()


class LinkTelegramView(APIView):
    """Эндпоинт для привязки Telegram‑аккаунта."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Привязка Telegram‑аккаунта к учётной записи Habit Tracker.",
        request_body=TelegramLinkSerializer,
        responses={
            "200": openapi.Response(
                description="Успешная привязка",
                examples={
                    "application/json": {
                        "message": "Telegram‑аккаунт успешно привязан!",
                        "test_sent": True,
                    }
                },
            ),
            "400": "Ошибка валидации",
        },
    )
    def post(self, request):
        user = request.user
        serializer = TelegramLinkSerializer(data=request.data)

        if serializer.is_valid():
            tg_chat_id = serializer.validated_data["tg_chat_id"]

            # Обновляем tg_chat_id в модели User (основное хранилище)
            user.tg_chat_id = tg_chat_id
            user.save()

            # Создаём или обновляем профиль в TelegramUser
            telegram_profile, created = TelegramUser.objects.update_or_create(
                user=user, defaults={"is_active": True}
            )

            # Отправляем тестовое сообщение
            test_sent = test_telegram_connection(tg_chat_id)

            if test_sent:
                return Response(
                    {
                        "message": "Telegram‑аккаунт успешно привязан!",
                        "test_sent": True,
                        "profile_created": created,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "message": "Аккаунт привязан, но тестовое сообщение не отправлено.",
                        "test_sent": False,
                        "profile_created": created,
                    },
                    status=status.HTTP_200_OK,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TelegramProfileView(APIView):
    """Просмотр и управление Telegram-профилем."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получить информацию о Telegram-профиле.",
        responses={
            "200": openapi.Response(
                description="Информация о профиле",
                examples={
                    "application/json": {
                        "is_active": True,
                        "tg_chat_id": "123456789",
                        "notification_time": "09:00:00",
                    }
                },
            ),
            "404": "Профиль не найден",
        },
    )
    def get(self, request):
        try:
            profile = request.user.telegram_profile
            return Response(
                {
                    "is_active": profile.is_active,
                    "tg_chat_id": request.user.tg_chat_id,
                    "notification_time": profile.notification_time,
                    "username": profile.username,
                    "first_name": profile.first_name,
                }
            )
        except TelegramUser.DoesNotExist:
            return Response(
                {
                    "is_active": False,
                    "tg_chat_id": request.user.tg_chat_id,
                    "notification_time": None,
                }
            )

    @swagger_auto_schema(
        operation_description="Обновить настройки Telegram-профиля.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "notification_time": openapi.Schema(
                    type=openapi.TYPE_STRING, format="time"
                ),
            },
        ),
        responses={"200": "Настройки обновлены"},
    )
    def patch(self, request):
        profile, created = TelegramUser.objects.get_or_create(user=request.user)

        if "is_active" in request.data:
            profile.is_active = request.data["is_active"]
        if "notification_time" in request.data:
            profile.notification_time = request.data["notification_time"]

        profile.save()

        return Response({"message": "Настройки обновлены"})


class UnlinkTelegramView(APIView):
    """Отвязка Telegram-аккаунта."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Отвязать Telegram-аккаунт.",
        responses={"200": "Аккаунт отвязан"},
    )
    def post(self, request):
        user = request.user
        user.tg_chat_id = None
        user.save()

        # Деактивируем профиль, но не удаляем
        try:
            profile = user.telegram_profile
            profile.is_active = False
            profile.save()
        except TelegramUser.DoesNotExist:
            pass

        return Response({"message": "Telegram-аккаунт отвязан"})
