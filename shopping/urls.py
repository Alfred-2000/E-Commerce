from django.urls import include, re_path
from rest_framework import routers

from shopping import views as ShoppingViews

router = routers.DefaultRouter()
router.register(
    r"product", ShoppingViews.ProductManagementViewSet, basename="product_management"
)
router.register(
    r"order", ShoppingViews.OrderManagementViewSet, basename="order_management"
)

urlpatterns = [
    re_path(r"^", include(router.urls)),
]
