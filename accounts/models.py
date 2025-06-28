from django.contrib.auth.models import AbstractUser
from django.db import models

from utils import models as UtilitiesModels


class MyUser(UtilitiesModels.CommonAttributes, AbstractUser):
    user_id = models.AutoField(primary_key=True)
    phone_code = models.CharField(max_length=6, null=True, blank=True)
    phone_number = models.TextField(blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.user_id} - {self.username}"


class Address(UtilitiesModels.CommonAttributes):
    user = models.ForeignKey("accounts.MyUser", on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True)
    landmark = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)


class UserSession(models.Model):
    session_id = models.UUIDField(primary_key=True, editable=False)
    user = models.ForeignKey(
        "accounts.MyUser", on_delete=models.CASCADE, related_name="sessions"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.session_id}"
