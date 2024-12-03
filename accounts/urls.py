from django.urls import include, path, re_path
from rest_framework import routers

from accounts import views as AccountsViews

router = routers.DefaultRouter()

urlpatterns = [
    re_path(r"list/", AccountsViews.ListDeleteUsers.as_view(), name="accounts_list"),
    re_path(
        r"register/", AccountsViews.RegisterUser.as_view(), name="account-register"
    ),
    re_path(
        r"(?P<user_id>[\w-]+)/",
        AccountsViews.RetrieveUpdateDeleteUser.as_view(),
        name="manage_accounts",
    ),
]
