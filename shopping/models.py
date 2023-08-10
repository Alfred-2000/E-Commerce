
import logging
from django.db import models
from datetime import datetime
from accounts.models import User
from django.db.models import DateTimeField
from django.dispatch import receiver
from django.db.models.signals import post_save


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_created = DateTimeField(null=True, blank=True)
    date_updated = DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    user_id = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    date_placed = DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=150)
    
    def __int__(self):
        return self.user_id


class OrderItem(models.Model):
    order_id = models.ForeignKey('shopping.Order', on_delete=models.CASCADE)
    product_id = models.ForeignKey('shopping.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)

    def __int__(self):
        return self.order_id


