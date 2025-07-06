from django.db import models

from shopping.constants import OrderStatus
from utils import models as UtilitiesModels


class Product(UtilitiesModels.CommonAttributes):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class ProductImage(UtilitiesModels.CommonAttributes):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_images"
    )
    image = models.ImageField(upload_to="product_images/")

    def __str__(self):
        return f"Image for {self.product.name}"


class Review(UtilitiesModels.CommonAttributes):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey("accounts.MyUser", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    review_text = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-created_at"]


class Order(UtilitiesModels.CommonAttributes):
    order_status = models.CharField(
        max_length=250, choices=OrderStatus.choices(), default=OrderStatus.ORDER_PLACED
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    user = models.ForeignKey("accounts.MyUser", on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class CartItems(UtilitiesModels.CommonAttributes):
    user = models.ForeignKey("accounts.MyUser", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class WishlistItems(UtilitiesModels.CommonAttributes):
    user = models.ForeignKey("accounts.MyUser", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
