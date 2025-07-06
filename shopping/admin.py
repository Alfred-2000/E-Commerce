from django.contrib import admin

from shopping.models import (
    CartItems,
    Order,
    Product,
    ProductImage,
    Review,
    WishlistItems,
)

admin.site.register(Order)
admin.site.register(Product)
admin.site.register(CartItems)
admin.site.register(WishlistItems)
admin.site.register(ProductImage)
admin.site.register(Review)
