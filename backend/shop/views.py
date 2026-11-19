from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsOwnerOrAdmin, is_admin_user

from .models import Category, Order, Product
from .serializers import (
    CategorySerializer,
    OrderCreateSerializer,
    OrderSerializer,
    ProductSerializer,
    ReviewSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/categories/ — публичный справочник категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Каталог товаров. Доступен без авторизации.

    Поддерживает:
      * ?category=<slug|id> — фильтрация по категории;
      * ?search=<строка>     — поиск по названию;
      * ?ordering=price|-price|name|-name|-created_at — сортировка.
    """

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Только активные товары; select_related убирает N+1 при выводе категории.
        qs = Product.objects.filter(is_active=True).select_related("category")
        params = self.request.query_params

        category = params.get("category")
        if category:
            if category.isdigit():
                qs = qs.filter(category_id=category)
            else:
                qs = qs.filter(category__slug=category)

        search = params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)

        ordering = params.get("ordering")
        if ordering in {"price", "-price", "name", "-name", "-created_at"}:
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by("name")
        return qs

    @action(detail=True, methods=["get", "post"], url_path="reviews")
    def reviews(self, request, pk=None):
        """GET — публичные отзывы товара; POST — отзыв от авторизованного пользователя."""
        product = self.get_object()

        if request.method == "GET":
            qs = product.reviews.select_related("user").order_by("-created_at")
            if not is_admin_user(request.user):
                # Гость и обычный пользователь видят только опубликованные отзывы.
                qs = qs.filter(is_published=True)
            return Response(ReviewSerializer(qs, many=True).data)

        if not request.user.is_authenticated:
            return Response(
                {"detail": "Требуется авторизация."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Заказы. Пользователь видит только свои, администратор — все."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.select_related("user").prefetch_related("items__product")
        if is_admin_user(self.request.user):
            return qs
        return qs.filter(user=self.request.user)

    def get_permissions(self):
        # Просмотр конкретного заказа — только владелец или администратор.
        if self.action == "retrieve":
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            OrderSerializer(order).data, status=status.HTTP_201_CREATED
        )
