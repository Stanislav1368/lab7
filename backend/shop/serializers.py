from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from .models import Category, Order, OrderItem, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "image",
            "stock",
            "is_active",
            "category",
            "category_name",
            "created_at",
        )

    def get_image(self, obj):
        # Возвращаем относительный URL (/media/...), чтобы он одинаково работал
        # и через прокси Vite, и при прямом обращении к Django.
        return obj.image.url if obj.image else None


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "product",
            "user",
            "username",
            "rating",
            "text",
            "is_published",
            "created_at",
        )
        # Автора и товар нельзя подставить из тела запроса — их задаёт вьюха.
        read_only_fields = ("product", "user", "is_published")


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "quantity", "price")


class OrderSerializer(serializers.ModelSerializer):
    """Только чтение: используется в списке и при ответе на создание заказа."""

    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "username",
            "status",
            "status_display",
            "total_price",
            "address",
            "created_at",
            "items",
        )


class OrderItemInputSerializer(serializers.Serializer):
    """Входная позиция корзины: товар + количество."""

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True)
    )
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    """Создание заказа: адрес + список позиций.

    Сумму и цены считает сервер по актуальному прайсу — фронтенду не доверяем.
    """

    address = serializers.CharField()
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Корзина пуста.")

        # Если один товар встречается несколько раз — суммируем количество.
        merged: dict[int, dict] = {}
        for item in items:
            product = item["product"]
            if product.pk in merged:
                merged[product.pk]["quantity"] += item["quantity"]
            else:
                merged[product.pk] = {
                    "product": product,
                    "quantity": item["quantity"],
                }

        for item in merged.values():
            if item["product"].stock < item["quantity"]:
                raise serializers.ValidationError(
                    f"Недостаточно товара «{item['product'].name}» на складе."
                )

        return list(merged.values())

    def create(self, validated_data):
        user = self.context["request"].user
        total = Decimal("0")

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                address=validated_data["address"],
                total_price=Decimal("0"),
            )
            for item in validated_data["items"]:
                # select_for_update защищает остаток от гонок при одновременных заказах.
                product = Product.objects.select_for_update().get(pk=item["product"].pk)
                quantity = item["quantity"]

                if product.stock < quantity:
                    raise serializers.ValidationError(
                        f"Недостаточно товара «{product.name}» на складе."
                    )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )
                product.stock -= quantity
                product.save(update_fields=("stock", "updated_at"))
                total += product.price * quantity

            order.total_price = total
            order.save(update_fields=("total_price", "updated_at"))

        return order
