from django.contrib import admin

from .models import Category, Order, OrderItem, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "stock", "is_active")
    list_filter = ("category", "is_active")
    list_editable = ("price", "stock", "is_active")
    search_fields = ("name", "description")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("price",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "address")
    inlines = (OrderItemInline,)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "is_published", "created_at")
    list_filter = ("is_published", "rating")
    list_editable = ("is_published",)
    search_fields = ("text", "product__name", "user__username")
