from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from config.base_models import BaseModel


class Category(BaseModel):
    """Категория кофе: зерно, молотый, капсулы и т.п."""

    name = models.CharField("Название", max_length=100, unique=True)
    slug = models.SlugField("Слаг", max_length=100, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Product(BaseModel):
    """Товар каталога. Связь: Category 1—N Product."""

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категория",
    )
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    image = models.ImageField(
        "Изображение", upload_to="products/", blank=True, null=True
    )
    stock = models.PositiveIntegerField("Остаток", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Order(BaseModel):
    """Заказ пользователя. Связь: User 1—N Order, Order 1—N OrderItem."""

    class Status(models.TextChoices):
        NEW = "new", "Новый"
        PAID = "paid", "Оплачен"
        SHIPPED = "shipped", "Отправлен"
        DONE = "done", "Выполнен"
        CANCELLED = "cancelled", "Отменён"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь",
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW
    )
    total_price = models.DecimalField(
        "Сумма", max_digits=10, decimal_places=2, default=0
    )
    address = models.TextField("Адрес доставки")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Заказ №{self.pk} — {self.user}"


class OrderItem(BaseModel):
    """Позиция заказа. Связи: Order 1—N OrderItem, Product 1—N OrderItem."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField("Количество", default=1)
    # Цену фиксируем на момент заказа, чтобы изменения прайса не меняли историю.
    price = models.DecimalField("Цена на момент заказа", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"
        ordering = ("id",)

    def __str__(self):
        return f"{self.product} × {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class Review(BaseModel):
    """Отзыв к товару. Связи: Product 1—N Review, User 1—N Review."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Товар",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Пользователь",
    )
    rating = models.PositiveSmallIntegerField(
        "Оценка",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    text = models.TextField("Текст отзыва")
    # По умолчанию отзыв публикуется сразу; администратор может снять публикацию в админке.
    is_published = models.BooleanField("Опубликован", default=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.product} — {self.rating}/5"
