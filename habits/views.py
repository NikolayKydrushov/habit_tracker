from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwner
from .paginations import StandardResultsSetPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с привычками пользователя."""
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Возвращает только привычки текущего пользователя."""
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить список своих привычек.",
        responses={
            '200': HabitSerializer(many=True),
            '401': 'Неавторизованный доступ'
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать новую привычку.",
        request_body=HabitSerializer,
        responses={
            '201': HabitSerializer,
            '400': 'Ошибка валидации данных'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class PublicHabitListView(generics.ListAPIView):
    """View для просмотра публичных привычек других пользователей."""
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Возвращает публичные привычки, исключая свои."""
        return Habit.objects.filter(
            is_public=True
        ).exclude(
            user=self.request.user
        ).select_related('user')  # Оптимизация запроса

    @swagger_auto_schema(
        operation_description="Получить список публичных привычек других пользователей.",
        responses={
            '200': HabitSerializer(many=True),
            '401': 'Неавторизованный доступ'
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)