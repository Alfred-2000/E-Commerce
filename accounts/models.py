from django.db import models
from datetime import datetime
from system.utils import DateTimeWithTZField
    
class Myuser(models.Model):
    user_id = models.UUIDField(primary_key=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.CharField(max_length=256, null=True, blank=True, unique=True)
    phone_code = models.CharField(max_length=6, null=True, blank=True)
    phone_number = models.TextField(blank=True, null=True, unique=True)
    is_superuser = models.BooleanField(default=False)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    created_at = DateTimeWithTZField(default=datetime.now(), null=True, blank=True)
    updated_at = DateTimeWithTZField(null=True, blank=True)

    def __str__(self):
        return self.username
