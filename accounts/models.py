import uuid
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from system.utils import DateTimeWithTZField


class MyUser(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    phone_code = models.CharField(max_length=6, null=True, blank=True)
    phone_number = models.TextField(blank=True, null=True, unique=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    created_at = DateTimeWithTZField(default=datetime.now(), null=True, blank=True)
    updated_at = DateTimeWithTZField(null=True, blank=True)

    def __str__(self):
        return self.username
