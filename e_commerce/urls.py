"""
URL configuration for e_commerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, re_path
from accounts import views as AccountsViews
from shopping import views as ShoppingViews

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^api/login/", AccountsViews.LoginView.as_view(), name="login"),
    re_path(r"^api/account/", include("accounts.urls")),
    re_path(r"^api/products/", ShoppingViews.ListCreateProducts.as_view()),
    re_path(
        r"^api/products/(?P<product_id>[\w-]+)/",
        ShoppingViews.RetrieveUpdateDeleteProducts.as_view(),
    ),
    re_path(r"^api/orders/", ShoppingViews.ListCreateOrders.as_view()),
    re_path(
        r"^api/orders/(?P<order_id>[\w-]+)/",
        ShoppingViews.RetrieveUpdateDeleteOrders.as_view(),
    ),
]
