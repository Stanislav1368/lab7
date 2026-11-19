"""
Выгрузка отчётов в XLSX (только для администратора).

Администратор присылает JSON вида:
    {"tables": {"products": ["id", "name", "price"],
                "orders":   ["id", "status", "total_price"]}}

Сервер проверяет имена таблиц и полей по «белому списку» TABLES,
формирует книгу openpyxl (каждая таблица — отдельный лист) и отдаёт файл.

Почему белый список:
  * защита от SQL-инъекций и обращения к служебным полям (например, password);
  * данные всё равно читаются через ORM (values(*fields)), raw()/extra() не используются;
  * фронтенд получает готовый список доступных таблиц/полей из /api/reports/schema/.
"""
from datetime import datetime

from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Order, OrderItem, Product, Review
from users.models import User
from users.permissions import IsAdminRole

# Описание доступных отчётов: ключ таблицы -> модель, подпись и разрешённые поля.
TABLES = {
    "products": {
        "label": "Товары",
        "model": Product,
        "fields": {
            "id": "ID",
            "name": "Название",
            "category__name": "Категория",
            "price": "Цена",
            "stock": "Остаток",
            "is_active": "Активен",
            "created_at": "Создан",
        },
    },
    "orders": {
        "label": "Заказы",
        "model": Order,
        "fields": {
            "id": "ID",
            "user__username": "Пользователь",
            "status": "Статус",
            "total_price": "Сумма",
            "address": "Адрес",
            "created_at": "Создан",
        },
    },
    "order_items": {
        "label": "Позиции заказов",
        "model": OrderItem,
        "fields": {
            "id": "ID",
            "order__id": "Заказ",
            "product__name": "Товар",
            "quantity": "Количество",
            "price": "Цена",
            "created_at": "Создан",
        },
    },
    "reviews": {
        "label": "Отзывы",
        "model": Review,
        "fields": {
            "id": "ID",
            "product__name": "Товар",
            "user__username": "Пользователь",
            "rating": "Оценка",
            "text": "Текст",
            "is_published": "Опубликован",
            "created_at": "Создан",
        },
    },
    "users": {
        "label": "Пользователи",
        "model": User,
        "fields": {
            "id": "ID",
            "username": "Логин",
            "email": "Email",
            "role": "Роль",
            "is_active": "Активен",
            "date_joined": "Дата регистрации",
        },
    },
}


class ReportSchemaView(APIView):
    """GET /api/reports/schema/ — список таблиц и полей для формы на фронтенде."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        tables = [
            {
                "key": key,
                "label": config["label"],
                "fields": [
                    {"key": field, "label": label}
                    for field, label in config["fields"].items()
                ],
            }
            for key, config in TABLES.items()
        ]
        return Response({"tables": tables})


class ExportReportView(APIView):
    """POST /api/reports/export/ — формирует и отдаёт .xlsx."""

    permission_classes = [IsAdminRole]

    def post(self, request):
        tables = request.data.get("tables")
        if not isinstance(tables, dict) or not tables:
            return Response(
                {"detail": "Поле tables обязательно и не должно быть пустым."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Валидация запроса по белому списку.
        selected: list[tuple[str, list[str]]] = []
        for table_key, fields in tables.items():
            if table_key not in TABLES:
                return Response(
                    {"detail": f"Неизвестная таблица: {table_key}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not isinstance(fields, list) or not fields:
                return Response(
                    {"detail": f"Для таблицы {table_key} не выбраны поля."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            allowed_fields = TABLES[table_key]["fields"]
            invalid = [field for field in fields if field not in allowed_fields]
            if invalid:
                return Response(
                    {
                        "detail": (
                            f"Недопустимые поля для {table_key}: "
                            f"{', '.join(map(str, invalid))}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            selected.append((table_key, fields))

        # 2. Формирование книги: каждая выбранная таблица — отдельный лист.
        workbook = Workbook()
        workbook.remove(workbook.active)  # убираем пустой лист по умолчанию

        for table_key, fields in selected:
            config = TABLES[table_key]
            worksheet = workbook.create_sheet(title=config["label"][:31])
            worksheet.append([config["fields"][field] for field in fields])

            # Имена полей уже проверены по белому списку, ORM сам экранирует значения.
            rows = config["model"].objects.order_by("id").values(*fields)
            for row in rows:
                worksheet.append([self._cell_value(row[field]) for field in fields])

            worksheet.freeze_panes = "A2"

        filename = f"coffee_report_{timezone.now():%Y%m%d_%H%M%S}.xlsx"
        response = HttpResponse(
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        workbook.save(response)
        return response

    @staticmethod
    def _cell_value(value):
        # openpyxl не умеет писать timezone-aware datetime — приводим к локальному
        # времени и убираем tzinfo.
        if isinstance(value, datetime) and timezone.is_aware(value):
            return timezone.localtime(value).replace(tzinfo=None)
        return value
