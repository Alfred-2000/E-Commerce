from django.db import models
from e_commerce.constants import ORDER_STATUS
from utilities import models as UtilitiesModels


class Product(UtilitiesModels.CommonAttributes):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name


class Order(UtilitiesModels.CommonAttributes):
    order_status = models.CharField(max_length=250, default=ORDER_STATUS[0])
    product_id = models.ForeignKey("shopping.Product", on_delete=models.CASCADE)
    product_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    user_id = models.ForeignKey("accounts.MyUser", on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    def __int__(self):
        return self.user_id
