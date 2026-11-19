"""Корневые маршруты проекта."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/", include("shop.urls")),
    path("api/reports/", include("reports.urls")),
]

# В dev-режиме Django сам отдаёт загруженные картинки товаров.
# (В docker они лежат в volume media_data, наружу не пробрасываются.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
