from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)


def tokens_for_user(user: User) -> dict:
    """Формирует пару JWT для пользователя (регистрация без повторного логина)."""
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — регистрация + сразу выдача JWT."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = tokens_for_user(user)
        data["user"] = UserSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ — логин по username/password, ответ содержит access/refresh/user."""

    serializer_class = CustomTokenObtainPairSerializer


class MeView(generics.RetrieveAPIView):
    """GET /api/auth/me/ — данные текущего пользователя."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
