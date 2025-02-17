from django.urls import re_path, include
from rest_framework import routers

from shopping import views as ShoppingViews

router = routers.DefaultRouter()
router.register(
    r"product", ShoppingViews.ProductManagementViewSet, basename="product_management"
)

urlpatterns = [
    re_path(r"^", include(router.urls)),
]
