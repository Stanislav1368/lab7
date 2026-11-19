from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Публичное представление пользователя (без служебных полей)."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "is_staff")
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """Регистрация нового покупателя. Пароль хэшируется стандартным механизмом Django."""

    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    # Необязательное подтверждение пароля — если передано, должно совпадать.
    password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")

    def validate(self, attrs):
        if attrs.get("password2") and attrs["password2"] != attrs["password"]:
            raise serializers.ValidationError({"password2": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        # create_user сам вызывает set_password() -> стандартный хэш Django.
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            role=User.Role.USER,
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Логин: к стандартной паре access/refresh добавляем данные пользователя."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
