"""
Общая абстрактная модель проекта.

Все модели (User, Category, Product, Order, OrderItem, Review) наследуются
от BaseModel, поэтому у каждой записи автоматически есть created_at и updated_at.
"""
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)
