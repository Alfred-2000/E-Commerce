from django.db import models

from payments.constants import TransactionStatus
from shopping.models import Order
from utils import models as UtilitiesModels


class Transaction(UtilitiesModels.CommonAttributes):
    payment = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=50,
        choices=TransactionStatus.choices(),
        default=TransactionStatus.PENDING,
    )
    transaction_date = models.DateTimeField(auto_now_add=True)
    gateway_response = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
