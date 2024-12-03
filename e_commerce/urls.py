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
from accounts.views import LoginView
from django.contrib import admin
from django.urls import include, path, re_path
from shopping.views import (ListCreateOrders, ListCreateProducts,
                            RetrieveUpdateDeleteOrders,
                            RetrieveUpdateDeleteProducts)

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^api/login/", LoginView.as_view(), name="login"),
    re_path(r"^api/account/", include("accounts.urls")),
    re_path(r"^api/products/", ListCreateProducts.as_view()),
    re_path(
        r"^api/products/(?P<product_id>[\w-]+)/", RetrieveUpdateDeleteProducts.as_view()
    ),
    re_path(r"^api/orders/", ListCreateOrders.as_view()),
    re_path(r"^api/orders/(?P<order_id>[\w-]+)/", RetrieveUpdateDeleteOrders.as_view()),
]
