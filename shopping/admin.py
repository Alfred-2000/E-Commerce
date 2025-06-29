from django.contrib import admin

from shopping.models import CartItems, Order, Product, WishlistItems

admin.site.register(Order)
admin.site.register(Product)
admin.site.register(CartItems)
admin.site.register(WishlistItems)
