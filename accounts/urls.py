from django.urls import include, re_path
from rest_framework import routers

from accounts import views as AccountsViews

router = routers.DefaultRouter()
router.register(
    r"user", AccountsViews.UserManagementViewSet, basename="user_management"
)

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(
        r"register/", AccountsViews.RegisterUser.as_view(), name="account_register"
    ),
]
