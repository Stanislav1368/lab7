"""Необязательная команда для быстрого наполнения каталога демо-данными.

Запуск: docker compose exec backend python manage.py seed_demo
"""
from django.core.management.base import BaseCommand

from shop.models import Category, Product

CATEGORIES = [
    ("Зерновой кофе", "zerno"),
    ("Молотый кофе", "molotyy"),
    ("Капсулы", "kapsuly"),
]

PRODUCTS = [
    {
        "name": "Arabica Ethiopia 250 г",
        "category": "zerno",
        "price": "790.00",
        "stock": 25,
        "description": "Светлая обжарка, ноты цитрусов и жасмина.",
    },
    {
        "name": "Arabica Colombia 250 г",
        "category": "zerno",
        "price": "720.00",
        "stock": 30,
        "description": "Сбалансированный вкус, карамель и орехи.",
    },
    {
        "name": "Espresso Blend 250 г",
        "category": "zerno",
        "price": "640.00",
        "stock": 40,
        "description": "Плотный бленд для эспрессо: шоколад и специи.",
    },
    {
        "name": "Молотый Filter Blend 250 г",
        "category": "molotyy",
        "price": "580.00",
        "stock": 18,
        "description": "Помол под воронку, ягодная кислинка.",
    },
    {
        "name": "Молотый Decaf 250 г",
        "category": "molotyy",
        "price": "610.00",
        "stock": 12,
        "description": "Без кофеина, мягкий вкус какао.",
    },
    {
        "name": "Капсулы Lungo (10 шт.)",
        "category": "kapsuly",
        "price": "450.00",
        "stock": 50,
        "description": "Для капсульных кофемашин, интенсивность 6.",
    },
    {
        "name": "Капсулы Ristretto (10 шт.)",
        "category": "kapsuly",
        "price": "470.00",
        "stock": 35,
        "description": "Интенсивность 10, насыщенный эспрессо.",
    },
]


class Command(BaseCommand):
    help = "Заполняет базу демонстрационными категориями и товарами"

    def handle(self, *args, **options):
        for name, slug in CATEGORIES:
            Category.objects.get_or_create(slug=slug, defaults={"name": name})

        categories = {c.slug: c for c in Category.objects.all()}

        created = 0
        for data in PRODUCTS:
            _, was_created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "category": categories[data["category"]],
                    "price": data["price"],
                    "stock": data["stock"],
                    "description": data["description"],
                },
            )
            created += int(was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: категорий — {len(CATEGORIES)}, новых товаров — {created}."
            )
        )
