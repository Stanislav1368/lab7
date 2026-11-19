from django.contrib.auth.models import AbstractUser
from django.db import models

from config.base_models import BaseModel


class User(BaseModel, AbstractUser):
    """Кастомная модель пользователя (AUTH_USER_MODEL = 'users.User').

    Роль определяет доступ к функционалу:
      * guest — неавторизованный посетитель (значение существует только для UI,
        в базе такие пользователи не создаются);
      * user  — зарегистрированный покупатель;
      * admin — администратор (Django admin + выгрузка отчётов XLSX).
    """

    class Role(models.TextChoices):
        GUEST = "guest", "Гость"
        USER = "user", "Пользователь"
        ADMIN = "admin", "Администратор"

    role = models.CharField(
        "Роль", max_length=10, choices=Role.choices, default=Role.USER
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        # Суперпользователь, созданный через createsuperuser, всегда администратор.
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    @property
    def is_admin_role(self) -> bool:
        return self.is_superuser or self.is_staff or self.role == self.Role.ADMIN
