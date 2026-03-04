from django.core.validators import MinLengthValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        validators=[
            MinLengthValidator(8, message="Пароль должен содержать минимум 8 символов.")
        ],
    )
    confirm_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "confirm_password")
        extra_kwargs = {
            "email": {"required": True, "allow_blank": False},
            "username": {"required": True, "allow_blank": False},
        }

    def validate(self, data):
        """Проверка совпадения паролей"""
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Пароли не совпадают.")
        return data

    def validate_email(self, value):
        """Проверка уникальности email."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate_username(self, value):
        """Проверка длины username."""
        if len(value) < 3:
            raise serializers.ValidationError(
                "Имя пользователя должно содержать минимум 3 символа."
            )
        return value

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise serializers.ValidationError(
                "Необходимо указать 'username' и 'password'."
            )

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Неверное имя пользователя или пароль.")

        if not user.is_active:
            raise serializers.ValidationError("Пользователь деактивирован.")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "tg_chat_id": user.tg_chat_id,
            },
        }


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя (чтение/обновление)."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "tg_chat_id", "first_name", "last_name")
        read_only_fields = ("id",)
